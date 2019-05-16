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


# serial_numbers = ["206C35733948", #front
#                   "206230804648", #middle
#                   "207D35903948"] #back

odrives = [ ['front' , "206C35733948", [-1, -1, 1, -1]],
            ['middle', "206230804648", [ 1,  1, 1, -1][]],
            ['back'  , "207D35903948", [-1, -1, 1, -1]] ]

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
            odrive.axis0.requested_state = state
        except:
            pass
        try:
            odrive.axis1.requested_state = state
        except:
            pass

def get_data(odrive):
        return [odrive.vbus_voltage,
                odrive.axis0.motor.current_control.Iq_measured,
                odrive.axis1.motor.current_control.Iq_measured]


def run_odrive(name, serial_number, directions):
    print("looking for "+name+" odrive")
    odrive = odrive.find_any(serial_number=serial_number)
    print("found " +name+ " odrive")

    send_state(odrive, AXIS_STATE_IDLE)
    while True:
        try:
            msg = cmd.get()
            print(msg)
            clear_errors(odrive)

            if (msg['t'] == 0 and msg['f'] == 0):
                send_state(odrive, AXIS_STATE_IDLE)
            else:
                odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
                odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
                odrive.axis0.controller.vel_setpoint =  -msg['f'] - msg['t'] 
                odrive.axis1.controller.vel_setpoint =   msg['f'] - msg['t']
                odrive.axis0.watchdog_feed()
                odrive.axis1.watchdog_feed()

        except timeout:
            print("Sending safe command")
            send_state(odrive, AXIS_STATE_IDLE)
            odrive.axis0.controller.vel_setpoint = 0
            odrive.axis1.controller.vel_setpoint = 0
        except AttributeErro:
            print("Lost contact with "+name+" odrive!")
            odrive = odrive.find_any(serial_number=serial_number)
            print("found " + name + " odrive")

    send_state(odrive, AXIS_STATE_IDLE)
        except:
            print("shutting down "+ name)
            send_state(drive, AXIS_STATE_IDLE)
            odrive.axis0.controller.vel_setpoint = 0
            odrive.axis1.controller.vel_setpoint = 0
            raise

while True:
    try:
        msg = cmd.get()
        print(msg)

#    finally:
#        print("Fianlly shutting down")
#        send_state(front_odrive, AXIS_STATE_IDLE)
#        send_state(middle_odrive, AXIS_STATE_IDLE)
#        send_state(back_odrive, AXIS_STATE_IDLE)
#        middle_odrive.axis0.controller.vel_setpoint = 0
#        middle_odrive.axis1.controller.vel_setpoint = 0
#        front_odrive.axis0.controller.vel_setpoint = 0
#        front_odrive.axis1.controller.vel_setpoint = 0
#        back_odrive.axis0.controller.vel_setpoint = 0
#        back_odrive.axis1.controller.vel_setpoint = 0

