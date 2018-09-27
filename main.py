#!/usr/bin/env python3
import odrive
from UDPComms import Subscriber

a = Subscriber("f t", b"ff", 8830)

while True:
    try:
            msg = a.recv()
            odrv0.axis0.controller.vel_setpoint = msg.f + msg.f
            odrv0.axis1.controller.vel_setpoint = -(msg.f - msg.f)
    except:
        pass
        odrv0.axis0.controller.vel_setpoint = 0
        odrv0.axis1.controller.vel_setpoint = 0
        raise

