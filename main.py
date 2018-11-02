#!/usr/bin/env python3
import odrive
from odrive.enums import *

from UDPComms import Subscriber

a = Subscriber("f t", b"ff", 8830, timeout = 0.3)

print("finding an odrives...")
middle_odrive = odrive.find_any(serial_number="208037853548")
front_odrive = odrive.find_any(serial_number="2062376E3548")
print("found")

middle_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
middle_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
front_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
front_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

while True:
    try:
        msg = a.recv()
        print(msg)
        if (msg.t == 0 and msg.f == 0):
            middle_odrive.axis0.requested_state = AXIS_STATE_IDLE
            middle_odrive.axis1.requested_state = AXIS_STATE_IDLE
            front_odrive.axis0.requested_state = AXIS_STATE_IDLE
            front_odrive.axis1.requested_state = AXIS_STATE_IDLE
        else:
            middle_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            middle_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            front_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            front_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

            middle_odrive.axis0.controller.vel_setpoint = -(msg.f + msg.t)
            middle_odrive.axis1.controller.vel_setpoint = (msg.f - msg.t)
            front_odrive.axis0.controller.vel_setpoint = (msg.f - msg.t)
            front_odrive.axis1.controller.vel_setpoint = -(msg.f + msg.t)
    except:
        middle_odrive.axis0.requested_state = AXIS_STATE_IDLE
        middle_odrive.axis1.requested_state = AXIS_STATE_IDLE
        front_odrive.axis0.requested_state = AXIS_STATE_IDLE
        front_odrive.axis1.requested_state = AXIS_STATE_IDLE
        middle_odrive.axis0.controller.vel_setpoint = 0
        middle_odrive.axis1.controller.vel_setpoint = 0
        front_odrive.axis0.controller.vel_setpoint = 0
        front_odrive.axis1.controller.vel_setpoint = 0
        raise

