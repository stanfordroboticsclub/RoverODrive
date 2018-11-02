#!/usr/bin/env python3
import odrive
from odrive.enums import *

from UDPComms import Subscriber
import time

a = Subscriber("f t", b"ff", 8830)

print("finding an odrives...")
middle_odrive = odrive.find_any(serial_number="208037853548")
front_odrive = odrive.find_any(serial_number="2062376E3548")
back_odrive = odrive.find_any(serial_number="208037843548")
print("found")

middle_odrive.axis0.requested_state = AXIS_STATE_IDLE
middle_odrive.axis1.requested_state = AXIS_STATE_IDLE
front_odrive.axis0.requested_state = AXIS_STATE_IDLE
front_odrive.axis1.requested_state = AXIS_STATE_IDLE
back_odrive.axis0.requested_state = AXIS_STATE_IDLE
back_odrive.axis1.requested_state = AXIS_STATE_IDLE

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
            middle_odrive.axis0.requested_state = AXIS_STATE_IDLE
            middle_odrive.axis1.requested_state = AXIS_STATE_IDLE
            front_odrive.axis0.requested_state = AXIS_STATE_IDLE
            front_odrive.axis1.requested_state = AXIS_STATE_IDLE
            back_odrive.axis0.requested_state = AXIS_STATE_IDLE
            back_odrive.axis1.requested_state = AXIS_STATE_IDLE
        else:
            middle_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            middle_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            front_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            front_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            back_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            back_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

            middle_odrive.axis0.controller.vel_setpoint = -(msg.f + msg.t)
            middle_odrive.axis1.controller.vel_setpoint = (msg.f - msg.t)
            front_odrive.axis0.controller.vel_setpoint = (msg.f - msg.t)
            front_odrive.axis1.controller.vel_setpoint = -(msg.f + msg.t)

            # back odrive is reversed left to right
            back_odrive.axis1.controller.vel_setpoint = (msg.f - msg.t)
            back_odrive.axis0.controller.vel_setpoint = -(msg.f + msg.t)
    except:
        pass
        middle_odrive.axis0.requested_state = AXIS_STATE_IDLE
        middle_odrive.axis1.requested_state = AXIS_STATE_IDLE
        front_odrive.axis0.requested_state = AXIS_STATE_IDLE
        front_odrive.axis1.requested_state = AXIS_STATE_IDLE
        back_odrive.axis0.requested_state = AXIS_STATE_IDLE
        back_odrive.axis1.requested_state = AXIS_STATE_IDLE
        middle_odrive.axis0.controller.vel_setpoint = 0
        middle_odrive.axis1.controller.vel_setpoint = 0
        front_odrive.axis0.controller.vel_setpoint = 0
        front_odrive.axis1.controller.vel_setpoint = 0
        back_odrive.axis0.controller.vel_setpoint = 0
        back_odrive.axis1.controller.vel_setpoint = 0
        raise

