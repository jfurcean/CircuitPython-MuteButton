# SPDX-FileCopyrightText: 2020 John Furcean
# SPDX-License-Identifier: MIT

import time
import board
from digitalio import DigitalInOut, Direction, Pull

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

import neopixel

# time you want to hold the button down before it changes states
BUTTON_HOLD_TIME = 1

# initialize onboard neopixel
# this will be used to indiciate what application is enabled
rgb_led = neopixel.NeoPixel(board.NEOPIXEL, 1)
rgb_led.brightness = 1.0
rgb_led[0] = (0, 0, 0)

kbd = Keyboard(usb_hid.devices)

# This will be used to indicate if muted or not
# please note that an individual will have to make sure it is synced with the application
button_led = DigitalInOut(board.D0)
button_led.direction = Direction.OUTPUT


# Digital input with pullup on D1
button1 = DigitalInOut(board.D1)
button1.direction = Direction.INPUT
button1.pull = Pull.UP

# Defines what the different states of the buttons will do

# Note: in order for the code to work appropriately,
# the keys need to start at 0 and increment upwards.
# Single keycodes commands need to have a trailing comma (,)
# the below keycode commands are for Mac and will need to be
# modified for Windows or Linux

controller_buttons = {

    0 : {
            'name': 'Space Bar',
            'keycode': (Keycode.SPACE,),
            'color':(0, 0, 0)
        },
    1 : {
            'name': 'Zoom Mute',
            'keycode': (Keycode.COMMAND, Keycode.SHIFT, Keycode.A),
            'color':(0, 0, 205)
        },
    2 : {
            'name': 'Teams Mute',
            'keycode': (Keycode.COMMAND, Keycode.SHIFT, Keycode.M),
            'color':(120, 0, 255)
        }

}

button1_in = False
button_index = 0
change_button = False



while True:

    # retreive the active controller button
    controller_button = controller_buttons[button_index%len(controller_buttons)]

    # set the color of the onboard neopixel to match the active controller button
    rgb_led[0] = controller_button['color']


    # detect if the button is recently pressed in
    if not button1.value and not button1_in:
        button_led.value = not button_led.value
        button1_in = True
        start_hold = time.monotonic()

    # detect if the button is being held down
    elif not button1.value and button1_in:
        time_now = time.monotonic()

        # change the state of the button controller if
        # the button has been held down for BUTTON_HOLD_TIME or more seconds
        if time_now - start_hold > BUTTON_HOLD_TIME and not change_button:
            print('Change State')
            button_index += 1
            start_hold = time.monotonic()
            button_led.value = False
            change_button = True


    # detect if the button has been released
    elif button1.value and button1_in:

        # execute the keyboard commands for the active button controller
        # if state of button controller hasn't been changed
        if not change_button:
            print("{} button press".format(controller_button['name']))
            kbd.send(*controller_button['keycode'])
            time.sleep(.1)

        # reset the change_button boolean if the state has been changed
        else:
            change_button = False

        # update the state of the button1_in Boolean
        button1_in = False