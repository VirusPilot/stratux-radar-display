#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
#
# BSD 3-Clause License
# Copyright (c) 2020, Thomas Breitbach
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
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

import math
import time
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
from . import radar_opts

# global constants
VERYLARGE = 24
LARGE = 18           # size of height indications of aircraft
SMALL = 12      # size of information indications on top and bottom
VERYSMALL = 10   # used for "nm" and "ft"
AIRCRAFT_SIZE = 3        # size of aircraft arrow
MINIMAL_CIRCLE = 10     # minimal size of mode-s circle
PITCH_SCALE = 0.5
# end definitions

# device properties
sizex = 0
sizey = 0
zerox = 0
zeroy = 0
verylargefont = ""
largefont = ""
smallfont = ""
verysmallfont = ""
webfont = ""
device = None
image = None
ahrs_image = None
ahrs_draw = None
roll_posmarks = (-90, -45, -30, -20, -10, 0, 10, 20, 30, 45, 90)
# end device globals


def posn(angle, arm_length):
    dx = round(math.cos(math.radians(angle)) * arm_length)
    dy = round(math.sin(math.radians(angle)) * arm_length)
    return dx, dy


def make_font(name, size):
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', name))
    return ImageFont.truetype(font_path, size)


def init():
    global sizex
    global sizey
    global zerox
    global zeroy
    global verylargefont
    global largefont
    global smallfont
    global verysmallfont
    global webfont
    global device
    global image

    config_path = str(Path(__file__).resolve().parent.joinpath('ssd1351.conf'))
    device = radar_opts.get_device(['-f', config_path])
    image = Image.new(device.mode, device.size)
    draw = ImageDraw.Draw(image)
    sizex = device.width
    sizey = device.height
    zerox = sizex / 2
    zeroy = sizey / 2
    device.contrast(255)  # set full contrast
    verylargefont = make_font("Font.ttc", VERYLARGE)
    largefont = make_font("Font.ttc", LARGE)          # font for height indications
    smallfont = make_font("Font.ttc", SMALL)          # font for information indications
    verysmallfont = make_font("Font.ttc", VERYSMALL)  # font for information indications
    webfont = make_font("fontawesome-webfont.ttf", SMALL)   # font for Bluetooth indications
    display_refresh = 0.1    # oled has no busy flag, so take this as update value
    return draw, sizex, zerox, zeroy, display_refresh


def cleanup():
    device.cleanup()


def centered_text(draw, y, text, font, fill):
    ts = draw.textsize(text, font)
    draw.text((zerox - ts[0] / 2, y), text, font=font, fill=fill)


def display():
    device.display(image)


def is_busy():
    # oled is never busy, no refresh
    return False


def next_arcposition(old_arcposition):
    # defines next position of height indicator on circle. Can be used to exclude several ranges or
    # be used to define the next angle on the circle
    return (old_arcposition + 210) % 360


def clear(draw):
    draw.rectangle((0, 0, sizex - 1, sizey - 1), fill="black")


def refresh():
    pass   # nothing to do for Oled, does not need a refresh function


def startup(draw, version, target_ip, seconds):
    logopath = str(Path(__file__).resolve().parent.joinpath('stratux-logo-64x64.bmp'))
    logo = Image.open(logopath)
    draw.rectangle(((0, 0), (sizex, 64)), fill="blue")
    draw.bitmap((zerox-32, 0), logo, fill="white")
    centered_text(draw, 64, "Oled-Radar", largefont, fill="white")
    versionstr = "Version " + version
    centered_text(draw, 64 + LARGE, versionstr, smallfont, fill="white")
    centered_text(draw, sizey - 2 * SMALL, "Connecting to", smallfont, fill="white")
    centered_text(draw, sizey - SMALL, target_ip, smallfont, fill="white")
    display()
    time.sleep(seconds)


def aircraft(draw, x, y, direction, height, vspeed, nspeed_length):
    p1 = posn(270 + direction, 2 * AIRCRAFT_SIZE)
    p2 = posn(270 + direction + 150, 4 * AIRCRAFT_SIZE)
    p3 = posn(270 + direction + 180, 2 * AIRCRAFT_SIZE)
    p4 = posn(270 + direction + 210, 4 * AIRCRAFT_SIZE)
    p5 = posn(270 + direction, nspeed_length)   # line for speed

    draw.polygon(((x + p1[0], y + p1[1]), (x + p2[0], y + p2[1]), (x + p3[0], y + p3[1]), (x + p4[0], y + p4[1])),
                 fill="red", outline="white")
    draw.line((x + p1[0], y + p1[1], x + p5[0], y + p5[1]), fill="white", width=1)
    if height >= 0:
        t = "+" + str(abs(height))
    else:
        t = "-" + str(abs(height))
    if vspeed > 0:
        t = t + '\u2191'
    if vspeed < 0:
        t = t + '\u2193'
    tsize = draw.textsize(t, largefont)
    if tsize[0] + x + 4 * AIRCRAFT_SIZE - 2 > sizex:
        # would draw text outside, move to the left
        tposition = (x - 4 * AIRCRAFT_SIZE - tsize[0], int(y - tsize[1] / 2))
    else:
        tposition = (x + 4 * AIRCRAFT_SIZE + 1, int(y - tsize[1] / 2))
    draw.rectangle((tposition, (tposition[0] + tsize[0], tposition[1] + tsize[1])), fill="black")
    draw.text(tposition, t, font=largefont, fill="white")


def modesaircraft(draw, radius, height, arcposition):
    if radius < MINIMAL_CIRCLE:
        radius = MINIMAL_CIRCLE
    draw.ellipse((64-radius, 64-radius, 64+radius, 64+radius), width=3, outline="white")
    arctext = posn(arcposition, radius)
    if height > 0:
        signchar = "+"
    else:
        signchar = "-"
    t = signchar+str(abs(height))
    tsize = draw.textsize(t, largefont)
    tposition = (64+arctext[0]-tsize[0]/2, 64+arctext[1]-tsize[1]/2)
    draw.rectangle((tposition, (tposition[0]+tsize[0], tposition[1]+tsize[1])), fill="black")
    draw.text(tposition, t, font=largefont, fill="white")


def situation(draw, connected, gpsconnected, ownalt, course, range, altdifference, bt_devices=0, sound_active=True):
    draw.ellipse((0, 0, sizex-1, sizey-1), outline="floralwhite")
    draw.ellipse((sizex/4, sizey/4, zerox + sizex/4, zeroy + sizey/4), outline="floralwhite")
    draw.ellipse((zerox-2, zeroy-2, zerox+2, zeroy+2), outline="floralwhite")
    draw.text((0, sizey - SMALL), "FL" + str(round(ownalt/100)), font=smallfont, fill="floralwhite")

    draw.text((0, 0), str(range), font=smallfont, fill="floralwhite")
    draw.text((0, SMALL), "nm", font=verysmallfont, fill="floralwhite")

    if altdifference >= 10000:
        t = str(int(altdifference/1000))+"k"
    else:
        t = str(altdifference)
    textsize = draw.textsize(t, smallfont)
    draw.text((sizex - textsize[0], 0), t, font=smallfont, fill="floralwhite", align="right")

    text = "ft"
    textsize = draw.textsize(text, smallfont)
    draw.text((sizex - textsize[0], SMALL), text, font=verysmallfont, fill="floralwhite", align="right")

    text = str(course) + '°'
    textsize = draw.textsize(text, smallfont)
    draw.text((sizex - textsize[0], sizey - textsize[1]), text, font=smallfont, fill="floralwhite", align="right")

    if bt_devices > 0:
        if sound_active:
            btcolor = "blue"
            text = '\uf293'  # bluetooth symbol + no
        else:
            btcolor = "red"
            text = '\uf1f6'  # bell off symbol
        textsize = draw.textsize(text, webfont)
        draw.text((sizex - textsize[0], sizey - 2*SMALL), text, font=webfont, fill=btcolor, align="right")

    if not gpsconnected:
        centered_text(draw, 0, "No GPS", smallfont, fill="red")
    if not connected:
        centered_text(draw, zeroy, "No Connection!", smallfont, fill="red")


def timer(draw, utctime, stoptime, laptime, laptime_head, left_text, middle_text, right_text, timer_runs):
    draw.text((0, 0), "UTC", font=smallfont, fill="cyan")
    centered_text(draw, SMALL, utctime, verylargefont, fill="yellow")
    draw.text((0, SMALL+VERYLARGE), "Timer", font=smallfont, fill="cyan")
    if timer_runs:
        color = "lavender"
    else:
        color = "orangered"
    centered_text(draw, 2*SMALL+VERYLARGE, stoptime, verylargefont, fill=color)
    draw.text((0, 2*SMALL + 2 * VERYLARGE), laptime_head, font=smallfont, fill="cyan")
    if laptime_head == "Laptimer":
        centered_text(draw, 3 * SMALL + 2 * VERYLARGE, laptime, verylargefont, fill="powderblue")
    else:
        centered_text(draw, 3 * SMALL + 2 * VERYLARGE, laptime, verylargefont, fill="magenta")

    draw.text((0, sizey - SMALL-3), left_text, font=smallfont, fill="green")
    textsize = draw.textsize(right_text, smallfont)
    draw.text((sizex - textsize[0], sizey - SMALL-3), right_text, font=smallfont, fill="green", align="right")
    centered_text(draw, sizey - SMALL-3, middle_text, smallfont, fill="green")


def shutdown(draw, countdown):
    message = "Shutdown "
    centered_text(draw, 10, message, largefont, fill="white")
    message = "in " + str(countdown) + " seonds!"
    centered_text(draw, 30, message, largefont, fill="white")
    message = "Press any button"
    centered_text(draw, 60, message, smallfont, fill="white")
    message = "to cancel ..."
    centered_text(draw, 80, message, smallfont, fill="white")


def init_ahrs():
    '''
    global ahrs_image
    global ahrs_draw

    maxpix = device.width * 6
    zero = device.width * 3
    ahrs_image = Image.new(device.mode, (maxpix, maxpix))
    ahrs_draw = ImageDraw.Draw(ahrs_image)

    ahrs_draw.rectangle((0, 0, maxpix, maxpix), fill="blue")   # sky
    ahrs_draw.rectangle((0, zero, maxpix, maxpix), fill="brown")  # earth
    ahrs_draw.line((0, zero, maxpix, zero), width=1, fill="white")  # horizon
    # pitch marks up
    i = 0
    while i < maxpix/2:
        i = i + 8
        if i % 16 == 0:
            ahrs_draw.line((zero-8, zero-i, zero+8, zero-i), width=1, fill="white")
            if i != 0:
                if i/8 <= 90:
                    marktext = str(i/16*10)
                else:
                    marktext = "80"
                ahrs_draw.text((zero-30, zero-i), marktext, font=verysmallfont, fill="white", align="right")
                ahrs_draw.text((zero+10, zero-i), marktext, font=verysmallfont, fill="white", align="left")
        else:
            ahrs_draw.line((zero-3, zero-i, zero+3, zero-i), width=1, fill="white")
    # pitch marks down
    i = 0
    while i < maxpix / 2:
        i = i + 8
        if i % 16 == 0:
            ahrs_draw.line((zero-8, zero+i, zero+8, zero+i), width=1, fill="white")
            if i != 0:
                if i / 8 <= 90:
                    marktext = str(i / 16 * 10)
                else:
                    marktext = "80"
                ahrs_draw.text((zero-30, zero+i), marktext, font=verysmallfont, fill="white", align="right")
                ahrs_draw.text((zero+10, zero+i), marktext, font=verysmallfont, fill="white", align="left")
        else:
            ahrs_draw.line((zero-3, zero+i, zero+3, zero+i), width=1, fill="white")
    '''


def rollmarks(draw, roll):
    draw.arc((0, 0, device.width, device.height), -roll+180, -roll, fill="white", width=1)
    draw.arc((16, 16, device.width-16, device.height-16), -roll + 180, -roll, fill = "white", width = 1)
    for rm in roll_posmarks:
        s = math.sin(math.radians(rm - roll))
        c = math.cos(math.radians(rm - roll))
        draw.line((zerox - zerox * c, zeroy - zerox * s, zerox - (zerox-16) * c, zeroy - (zerox-16) * s),
                  fill="white", width=1)
    draw.polygon((zerox, 16, zerox-8, 16+8, zerox+8, 16-8), fill="white")
    rolltext = str(roll)
    draw.text((zerox+4, 16+4), rolltext, font=smallfont, fill="white", align="right")


def ahrs(draw, pitch, roll, heading, slipskid):
    global image
    global ahrs_image

    print("AHRS: pitch ", pitch, " roll ", roll, " heading ", heading, " slipskid ", slipskid)
    # first do the translation on pitch
    y_line = zeroy + pitch * 2
    h = math.tan(math.radians(roll)) * device.width / 2
    x2 = device.width-1
    y2 = y_line - h
    x1 = 0
    y1 = y_line + h

    draw.polygon((x1, y1, 0, 0, device.width-1, 0, x2, y2), fill="blue")
    draw.polygon((x1, y1, 0, device.height-1, device.width-1, device.height-1, x2,y2), fill="brown")
    draw.line((x1, y1, x2, y2), fill="white", width=2)
    # pointer in the middle
    draw.line((zerox-30, zeroy, zerox-15, zeroy), width=4, fill="yellow")
    draw.line((zerox + 30, zeroy, zerox + 15, zeroy), width=4, fill="yellow")
    draw.polygon((zerox, zeroy+2, zerox-10, zeroy+8, zerox+10, zeroy+8), fill="yellow")

    rollmarks(draw, roll)

    infotext = "P:"+str(pitch)+" R:"+str(roll)
    draw.text((0, 100), infotext, font=smallfont, fill="white", align="right")

