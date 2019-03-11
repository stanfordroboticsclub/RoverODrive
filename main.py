#!/usr/bin/env python3
import odrive
from odrive.enums import *

from UDPComms import Subscriber, Publisher, timeout
import time

import os
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

cmd = Subscriber(8830, timeout = 0.3)
telemetry = Publisher(8810)

print("finding an odrives...")

front_odrive = odrive.find_any(serial_number="206230804648")
print("found front odrive")
middle_odrive = odrive.find_any(serial_number="206C35733948")
print("found middle odrive")
back_odrive = odrive.find_any(serial_number="207D35903948")
print("found back odrive")

print("found all odrives")

def clear_errors(odrive):
    if odrive.axis0.error:
        print("axis 0", odrive.axis0.error)
        odrive.axis0.error = 0
    if odrive.axis1.error:
        print("axis 1", odrive.axis1.error)
        odrive.axis1.error = 0

    if odrive.axis0.motor.error:
        print("motor 0", odrive.axis0.motor.error)
        odrive.axis0.motor.error = 0
    if odrive.axis1.motor.error:
        print("motor 1", odrive.axis1.motor.error)
        odrive.axis1.motor.error = 0

    if odrive.axis0.encoder.error:
        print("encoder 0", odrive.axis0.encoder.error)
        odrive.axis0.encoder.error = 0
    if odrive.axis1.encoder.error:
        print("encoder 1", odrive.axis1.encoder.error)
        odrive.axis1.encoder.error = 0

def send_state(odrive, state):
        try:
            odrive.axis0.requested_state = AXIS_STATE_IDLE
        except:
            pass
        try:
            odrive.axis1.requested_state = AXIS_STATE_IDLE
        except:
            pass
    

send_state(front_odrive, AXIS_STATE_IDLE)
send_state(middle_odrive, AXIS_STATE_IDLE)
send_state(back_odrive, AXIS_STATE_IDLE)

while True:
    try:
        msg = cmd.get()
        print(msg)

        try:
            telemetry.send( [middle_odrive.vbus_voltage,
                        front_odrive.axis0.motor.current_control.Iq_measured,
                        front_odrive.axis1.motor.current_control.Iq_measured,
                        middle_odrive.axis0.motor.current_control.Iq_measured,
                        middle_odrive.axis1.motor.current_control.Iq_measured,
                        back_odrive.axis0.motor.current_control.Iq_measured,
                        back_odrive.axis1.motor.current_control.Iq_measured] )
        except:
            pass

        clear_errors(front_odrive)
        clear_errors(middle_odrive)
        clear_errors(back_odrive)

        if (msg['t'] == 0 and msg['f'] == 0):
            send_state(front_odrive, AXIS_STATE_IDLE)
            send_state(middle_odrive, AXIS_STATE_IDLE)
            send_state(back_odrive, AXIS_STATE_IDLE)
        else:
            middle_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            middle_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            front_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            front_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            back_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            back_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

            front_odrive.axis0.controller.vel_setpoint = (-msg['f'] - msg['t'])
            front_odrive.axis1.controller.vel_setpoint = -(-msg['f'] + msg['t'])
            middle_odrive.axis0.controller.vel_setpoint = (msg['f'] + msg['t'])
            middle_odrive.axis1.controller.vel_setpoint = (msg['f'] - msg['t'])

            # back odrive is reversed left to right
            back_odrive.axis1.controller.vel_setpoint = (msg['f'] - msg['t'])
            back_odrive.axis0.controller.vel_setpoint = -(msg['f'] + msg['t'])

    except timeout:
        print("Sending safe command")
        send_state(front_odrive, AXIS_STATE_IDLE)
        send_state(middle_odrive, AXIS_STATE_IDLE)
        send_state(back_odrive, AXIS_STATE_IDLE)
        middle_odrive.axis0.controller.vel_setpoint = 0
        middle_odrive.axis1.controller.vel_setpoint = 0
        front_odrive.axis0.controller.vel_setpoint = 0
        front_odrive.axis1.controller.vel_setpoint = 0
        back_odrive.axis0.controller.vel_setpoint = 0
        back_odrive.axis1.controller.vel_setpoint = 0
    except:
        print("shutting down")
        send_state(front_odrive, axis_state_idle)
        send_state(middle_odrive, axis_state_idle)
        send_state(back_odrive, axis_state_idle)
        middle_odrive.axis0.controller.vel_setpoint = 0
        middle_odrive.axis1.controller.vel_setpoint = 0
        front_odrive.axis0.controller.vel_setpoint = 0
        front_odrive.axis1.controller.vel_setpoint = 0
        back_odrive.axis0.controller.vel_setpoint = 0
        back_odrive.axis1.controller.vel_setpoint = 0
        raise
    finally:
        print("Fianlly shutting down")
        send_state(front_odrive, axis_state_idle)
        send_state(middle_odrive, axis_state_idle)
        send_state(back_odrive, axis_state_idle)
        middle_odrive.axis0.controller.vel_setpoint = 0
        middle_odrive.axis1.controller.vel_setpoint = 0
        front_odrive.axis0.controller.vel_setpoint = 0
        front_odrive.axis1.controller.vel_setpoint = 0
        back_odrive.axis0.controller.vel_setpoint = 0
        back_odrive.axis1.controller.vel_setpoint = 0

