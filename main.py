#!/usr/bin/env python3
import odrive
from odrive.enums import *

from UDPComms import Subscriber

a = Subscriber("f t", b"ff", 8830)

print("finding an odrive...")
odrv0 = odrive.find_any()
print("found")

odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
odrv0.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

while True:
    try:
        msg = a.recv()
        print(msg)
        odrv0.axis0.controller.vel_setpoint = -(msg.f + msg.t)
        odrv0.axis1.controller.vel_setpoint = (msg.f - msg.t)
    except:
        pass
        odrv0.axis0.controller.vel_setpoint = 0
        odrv0.axis1.controller.vel_setpoint = 0
        raise

