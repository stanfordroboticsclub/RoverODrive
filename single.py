#!/usr/bin/env python3
import odrive
from odrive.enums import *

from UDPComms import Subscriber, timeout
import time

import os
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

a = Subscriber("f t", b"ff", 8830, timeout = 0.3)

print("finding any odrives...")
odrive = odrive.find_any()
print("found an odrive (random)")

odrive.axis0.requested_state = AXIS_STATE_IDLE
odrive.axis1.requested_state = AXIS_STATE_IDLE

while True:
    try:
        msg = a.get()
        print(msg)
        if (msg.t == 0 and msg.f == 0):
            odrive.axis0.requested_state = AXIS_STATE_IDLE
            odrive.axis1.requested_state = AXIS_STATE_IDLE
        else:
            odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

            odrive.axis0.controller.vel_setpoint = (msg.f + msg.t)
            odrive.axis1.controller.vel_setpoint = -(msg.f - msg.t)
    except timeout:
        odrive.axis0.requested_state = AXIS_STATE_IDLE
        odrive.axis1.requested_state = AXIS_STATE_IDLE
        odrive.axis0.controller.vel_setpoint = 0
        odrive.axis1.controller.vel_setpoint = 0
    except:
        odrive.axis0.requested_state = AXIS_STATE_IDLE
        odrive.axis1.requested_state = AXIS_STATE_IDLE
        odrive.axis0.controller.vel_setpoint = 0
        odrive.axis1.controller.vel_setpoint = 0
        raise

