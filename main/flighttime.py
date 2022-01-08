#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
#
# BSD 3-Clause License
# Copyright (c) 2022, Thomas Breitbach
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime
import logging
import json
import statusui
import radarbuttons


# constants
SPEED_THRESHOLD_TAKEOFF = 30    # threshold in kts, when flying is detected or stopped
SPEED_THRESHOLD_LANDING = 10    # threshold in kts, when landing is detected or stopped
SPEED_THRESHOLD_STOPPED = 5     # threshold in kts, when stopping is detected. Triggers display of flighttime
TRIGGER_PERIOD_TAKEOFF = 5
# min time in seconds threshold has to be met before takeoff is triggered (to compensate gps errors)
TRIGGER_PERIOD_LANDING = 5
# min time in seconds threshold has to be underrug before landing is triggered (to compensate gps errors)
TRIGGER_PERIOD_STOP = 10
# min time in seconds threshold has to be underrun before stop is triggered which will change display
FLIGHT_LIST_LENGTH = 10


# global variables
measurement_enabled = False
takeoff_time = None
landing_time = None
flying = False    # indicates if flying mode was detected and measurement starting
new_flight_info = False   # indicates whether a new flight was recorded, but not yet displayed
trigger_timestamp = None    # timestamp when threshold was overrun/underrun
stop_timestamp = None       # timestamp when stopping after a flight was detected, may start again or stop
switch_back_mode = 0        # mode to switch back when flying after automatic flighttime display is triggered
takeoff_delta = datetime.timedelta(seconds=TRIGGER_PERIOD_TAKEOFF)
landing_delta = datetime.timedelta(seconds=TRIGGER_PERIOD_LANDING)
stop_delta = datetime.timedelta(seconds=TRIGGER_PERIOD_STOP)
flighttime_changed = True
rlog = None
g_config = {}


def default(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()


def init(activated, config):
    global rlog
    global measurement_enabled
    global g_config

    rlog = logging.getLogger('stratux-radar-log')
    rlog.debug("Flighttime: time-measurement initialized")
    measurement_enabled = activated
    g_config = config
    if 'last_flights' in config:
        rlog.debug("Flighttime: Last flights read from config: " + json.dumps(config['last_flights'], indent=4,
                                                                              default=default))


def new_flight(flight):
    global g_config

    if 'last_flights' not in g_config:
        g_config['last_flights'] = []
    g_config['last_flights'].insert(0, flight)
    if len(g_config['last_flights']) > FLIGHT_LIST_LENGTH:
        del g_config['last_flights'][FLIGHT_LIST_LENGTH-1]


def current_starttime():
    if 'last_flights' in g_config and g_config['last_flights'][0][1] == 0:    # means we are in the air
            return g_config['last_fights'][0][0]
    return None


def trigger_measurement(valid_gps, situation, ahrs, current_mode):
    # called from situationhandler whenever new situation is received
    global trigger_timestamp
    global stop_timestamp
    global takeoff_time
    global landing_time
    global flying
    global new_flight_info
    global flighttime_changed
    global switch_back_mode

    if not valid_gps or not measurement_enabled:
        return 0
    now = datetime.datetime.now(datetime.timezone.utc)
    if not flying:
        if trigger_timestamp is None and situation['gps_speed'] >= SPEED_THRESHOLD_TAKEOFF:
            trigger_timestamp = now
            rlog.info("Flighttime: Takeoff threshold exceeded triggered at " + str(now))
        elif trigger_timestamp is not None and situation['gps_speed'] >= SPEED_THRESHOLD_TAKEOFF:
            if now - trigger_timestamp >= takeoff_delta:
                takeoff_time = now
                rlog.info("Flighttime: Takeoff detected at " + str(now))
                new_flight([now, 0])  # means not yet finished
                flighttime_changed = True
                flying = True
                trigger_timestamp = None
                if switch_back_mode != 0:
                    return switch_back_mode
        elif trigger_timestamp is not None and situation['gps_speed'] < SPEED_THRESHOLD_TAKEOFF:
            # reset trigger, not several seconds above threshold
            trigger_timestamp = None
            rlog.info("Flighttime: Threshold underrun, trigger resetted at " + str(now))
        if new_flight_info:   # no more flying, check whether stop is done
            if stop_timestamp is None and situation['gps_speed'] < SPEED_THRESHOLD_STOPPED:
                stop_timestamp = now
                print("Flighttime: Stop detection triggered at " + str(now))
            elif stop_timestamp is not None and situation['gps_speed'] < SPEED_THRESHOLD_STOPPED:
                if now - stop_timestamp >= stop_delta:
                    rlog.info("Flighttime: Stop detected at " + str(now))
                    stop_timestamp = None
                    new_flight_info = False   # stop is only triggered once
                    switch_back_mode = current_mode
                    return 17    # return mode set to display times
            elif stop_timestamp is not None and situation['gps_speed'] >= SPEED_THRESHOLD_STOPPED:
                # reset trigger, not several seconds below threshold
                stop_timestamp = None
                rlog.info("Flighttime: Stop threshold overrun, trigger resetted at " + str(now))
    else:   # flying
        flighttime_changed = True   # set in any case so display is refreshed
        if trigger_timestamp is None and situation['gps_speed'] < SPEED_THRESHOLD_LANDING:
            trigger_timestamp = now
            print("Flighttime: Landing threshold underrun triggered at " + str(now))
        elif trigger_timestamp is not None and situation['gps_speed'] < SPEED_THRESHOLD_LANDING:
            if now - trigger_timestamp >= landing_delta:
                landing_time = now
                rlog.info("Flighttime: Landing detected at " + str(now))
                g_config['last_flights'][0][1] = now
                statusui.write_config(g_config)
                flying = False
                new_flight_info = True
                trigger_timestamp = None
        elif trigger_timestamp is not None and situation['gps_speed'] >= SPEED_THRESHOLD_LANDING:
            # reset trigger, not several seconds above threshold
            trigger_timestamp = None
            rlog.info("Flighttime: Landing threshold overrun, trigger resetted at " + str(now))
    return 0


def draw_flighttime(draw, display_control, changed, config):
    global flighttime_changed

    if changed or flighttime_changed:
        flighttime_changed = False
        display_control.clear(draw)
        if 'last_flights' in config:
            last_flights = config['last_flights']
        else:
            last_flights = []
        display_control.flighttime(draw, last_flights)
        display_control.display()


def user_input():
    global flighttime_changed
    global switch_back_mode

    btime, button = radarbuttons.check_buttons()
    if btime == 0:
        return 0  # stay in current mode
    flighttime_changed = True
    switch_back_mode = 0    # cancel any switchback, if button was pressed
    if button == 1 and (btime == 1 or btime == 2):  # middle in any case
        return 1  # next mode to be radar
    if button == 0 and btime == 2:  # left and long
        return 3  # start next mode shutdown!
    if button == 2 and btime == 2:  # right and long- refresh
        return 18  # start next mode for display driver: refresh called
    return 17  # no mode change
