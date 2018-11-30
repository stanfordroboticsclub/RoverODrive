#!/usr/bin/env python3
import odrive
from odrive.enums import *

from UDPComms import Subscriber
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

# this makes sure there are no old messages queued up that can make
# the rover drive
first_msg = a.recv()
start_time = time.time()
while (time.time() - start_time) < 5:
    ignore_msg = a.recv()

while True:
    try:
        msg = a.recv()
        print(msg)
        if (msg.t == 0 and msg.f == 0):
            odrive.axis0.requested_state = AXIS_STATE_IDLE
            odrive.axis1.requested_state = AXIS_STATE_IDLE
        else:
            odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

            odrive.axis0.controller.vel_setpoint = (msg.f + msg.t)
            odrive.axis1.controller.vel_setpoint = -(msg.f - msg.t)
    except:
        odrive.axis0.requested_state = AXIS_STATE_IDLE
        odrive.axis1.requested_state = AXIS_STATE_IDLE
        odrive.axis0.controller.vel_setpoint = 0
        odrive.axis1.controller.vel_setpoint = 0
        raise

