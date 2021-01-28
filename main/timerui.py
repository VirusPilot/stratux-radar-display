#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
#
# BSD 3-Clause License
# Copyright (c) 2021, Thomas Breitbach
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

import time
import radarbuttons
import math

# constants
MAX_COUNTDOWN_TIME = 2 * 60 * 60   # maximum time for setting countdown in seconds

# global variables
left_text = ''
middle_text = 'Mode'
right_text = 'Start'
lap_head = 'Laptimer'

stoptime = 0
laptime = 0
timer_running = False
was_in_secs = 0.0       # last time displayed
timer_ui_changed = True
cdown_time = 0.0     # count down time
timer_mode = 0    # 0 = normal, 1 = countdown-set


def draw_timer(draw, display_control, refresh_time):
    global was_in_secs
    global timer_ui_changed

    now_in_secs = math.floor(time.time())
    if not timer_ui_changed and now_in_secs < was_in_secs + math.ceil(refresh_time):
        return    # nothing to display if time has not changed or change would be quicker than display
    was_in_secs = now_in_secs
    timer_ui_changed = False
    display_control.clear(draw)
    utctimestr = time.strftime("%H:%M:%S", time.gmtime(now_in_secs))
    if timer_running:
        stoptimestr = time.strftime("%H:%M:%S", time.gmtime(now_in_secs-stoptime))
        if laptime != 0:
            laptimestr = time.strftime("%H:%M:%S", time.gmtime(now_in_secs-laptime))
        else:
            if cdown_time == 0.0:
                laptimestr = "--:--:--"
            else:
                laptimestr = time.strftime("%H:%M:%S", time.gmtime(cdown_time))
    else:
        if stoptime != 0:
            stoptimestr = time.strftime("%H:%M:%S", time.gmtime(stoptime))
        else:
            stoptimestr = "--:--:--"
        if cdown_time <= 0.0:
            laptimestr = "--:--:--"
        else:
            laptimestr = time.strftime("%H:%M:%S", time.gmtime(cdown_time - now_in_secs))

    display_control.timer(draw, utctimestr, stoptimestr, laptimestr, lap_head, left_text, middle_text, right_text,
                          timer_running)
    display_control.display()


def user_input():
    global left_text
    global right_text
    global middle_text
    global stoptime
    global laptime
    global timer_running
    global timer_ui_changed
    global cdown_time
    global lap_head
    global timer_mode

    btime, button = radarbuttons.check_buttons()
    # start of timer global behaviour
    if btime == 0:
        return 2  # stay in timer mode
    timer_ui_changed = True
    if button == 1 and btime == 2:  # middle and long
        return 1  # next mode to be radar
    if button == 0 and btime == 2:  # left and long
        return 3  # start next mode shutdown!

    # situation dependent behauvior
    if timer_mode == 0:   # normal timer mode
        if button == 1 and btime == 1:   # middle and short
            timer_mode = 1
            cdown_time = 0
        if button == 2 and btime == 1:   # short right
            if timer_running:   # timer already running
                stoptime = math.floor(time.time()) - stoptime
                if cdown_time > 0:
                    cdown_time = cdown_time - math.floor(time.time())
                laptime = 0    # also stop lap time
                timer_running = False
            else:
                stoptime = math.floor(time.time()) - stoptime   # add time already on clock
                if cdown_time > 0:
                    cdown_time = math.floor(time.time()) + cdown_time
                laptime = 0
                timer_running = True
        if button == 0:   # left
            if btime == 2:  # left and long
                return 3    # start next mode shutdown!
            else:
                if timer_running:
                    laptime = math.floor(time.time())
                else:
                    stoptime = 0
                    laptime = 0
                    right_text = "Start"
                    left_text = ""
        # set display
        if timer_running:
            right_text = "Stop"
            left_text = "Lap"
        else:
            if stoptime == 0.0:
                right_text = "Start"
                left_text = ""
            else:
                right_text = "Cont"
                left_text = "Reset"
    elif timer_mode == 1:   # countdown set mode
        lap_head = "Set Countdown"
        right_text = "+1m"
        left_text = "+10m"
        if button == 1 and btime == 1:   # middle and short
            if cdown_time > 0:
                laptime = 0  # stop laptimer and do countdown
                lap_head = "Countdown"
            else:
                lap_head = "Laptimer"
            timer_mode = 0
        elif button == 0 and btime == 1:  # left short
            cdown_time = cdown_time + 600   # ten more minutes
            if cdown_time >= MAX_COUNTDOWN_TIME:
                cdown_time = 0
        elif button == 2 and btime == 1:  # right short
            cdown_time = cdown_time + 60
            if cdown_time >= MAX_COUNTDOWN_TIME:
                cdown_time = 0

    timer_ui_changed = True
    return 2   # no mode change
