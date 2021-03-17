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

import radarbuttons
import logging
import requests

# constants
MSG_NO_CONNECTION = "NO CONNECTION!"
# globals
url_gmeter_reset = ""


def init(url):
    global url_gmeter_reset

    url_gmeter_reset = url
    logging.debug("GMeterUI: Initialized POST settings to " + url_gmeter_reset)


def reset_gmeter():
    logging.debug("GMeterUI: Reset gmeter triggered")
    try:
        requests.post(url_gmeter_reset)
    except requests.exceptions.RequestException as e:
        logging.debug("Posting gmeter-reset exception: ", e)


def draw_gmeter(draw, display_control, connected, gmeter):
    if gmeter['was_changed']:
        gmeter['was_changed'] = False
        error_message = None
        if not connected:
            error_message = MSG_NO_CONNECTION
        display_control.clear(draw)
        display_control.gmeter(draw, gmeter['current'], gmeter['max'], gmeter['min'], error_message)
        display_control.display()


def user_input():
    btime, button = radarbuttons.check_buttons()
    # start of ahrs global behaviour
    if btime == 0:
        return 0  # stay in current mode
    if button == 1 and btime == 2:  # middle and long
        return 1  # next mode to be radar
    if button == 0 and btime == 2:  # left and long
        return 3  # start next mode shutdown!
    if button == 2 and btime == 2:  # right and long- refresh
        return 10  # start next mode for display driver: refresh called from gmeter
    if button == 2 and btime == 1:  # right and short - reset
        reset_gmeter()
        return 9
    return 9  # no mode change
