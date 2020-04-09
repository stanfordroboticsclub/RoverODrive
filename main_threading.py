#!/usr/bin/env python3
import odrive
from odrive.enums import *
from fibre.protocol import ChannelBrokenException
from usb.core import USBError

from UDPComms import Subscriber, Publisher, timeout

import os
import threading
import time
import math


if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

cmd = Subscriber(8830, timeout = 0.5)
telemetry = Publisher(8810)

# motor 0 is right
# motor 1 is left
odrives = [ ['single' , "376136493137", [-1, 1]] ]

def clear_errors(odv):
    if odv.axis0.error:
        print("axis 0", odv.axis0.error)
        odv.axis0.error = 0
    if odv.axis1.error:
        print("axis 1", odv.axis1.error)
        odv.axis1.error = 0

    if odv.axis0.motor.error:
        print("motor 0", odv.axis0.motor.error)
        odv.axis0.motor.error = 0
    if odv.axis1.motor.error:
        print("motor 1", odv.axis1.motor.error)
        odv.axis1.motor.error = 0

    if odv.axis0.encoder.error:
        print("encoder 0", odv.axis0.encoder.error)
        odv.axis0.encoder.error = 0
    if odv.axis1.encoder.error:
        print("encoder 1", odv.axis1.encoder.error)
        odv.axis1.encoder.error = 0

def send_state(odv, state):
        try:
            odv.axis0.requested_state = state
        except:
            pass
        try:
            odv.axis1.requested_state = state
        except:
            pass

def get_data(odv):
        WHEEL_RAD = 6.5 * 25.4 /2
        WHEEL_BASE = 18 * 25.4

        rev0 = -odv.axis0.encoder.vel_estimate / odv.axis0.encoder.config.cpr
        rev1 =  odv.axis1.encoder.vel_estimate / odv.axis1.encoder.config.cpr

        dist0 = 2 * math.pi * WHEEL_RAD * rev0
        dist1 = 2 * math.pi * WHEEL_RAD * rev1

        #motor 0 is right
        dx =  (dist0 + dist1)/2
        da = (dist0 - dist1)/WHEEL_BASE

        return {"vbus":odv.vbus_voltage,
                "cur": [odv.axis0.motor.current_control.Iq_measured,
                odv.axis1.motor.current_control.Iq_measured],
                "odom": [da,dx] }

def atomic_print(s):
    print(str(s)+'\n',end='')


def run_odrive(name, serial_number, d):
    atomic_print("looking for "+name+" odrive")
    odv = odrive.find_any(serial_number=serial_number)
    atomic_print("found " +name+ " odrive")
    send_state(odv, AXIS_STATE_IDLE)

    try:
        while True:
            # read from USB Block
            lostConnection = True
            try:
                UDPLock.acquire()
                msg = cmd.get()
                atomic_print(msg)
                lostConnection = False
            except timeout:
                lostConnection = True
                msg = {'t':0, 'f':0}
            finally:
                UDPLock.release()

            # Write to Odrives block
            try:
                clear_errors(odv)
                if lostConnection:
                # if msg['f'] == 0 and msg['t'] == 0:
                    atomic_print("Timeout sending safe")
                    send_state(odv, AXIS_STATE_IDLE)
                else:
                    send_state(odv, AXIS_STATE_CLOSED_LOOP_CONTROL)
                    # axis 0 (right) is always same sign
                    # axis 1 (left) is always opposite sign
                    odv.axis0.controller.vel_setpoint =  d[0]*( \
                                msg['f'] - msg['t'])
                    odv.axis1.controller.vel_setpoint =  d[1]*( \
                                msg['f'] + msg['t'])
                    odv.axis0.watchdog_feed()
                    odv.axis1.watchdog_feed()

                tele[name] = get_data(odv)

            except (USBError, ChannelBrokenException) as e:
                atomic_print("Lost contact with "+name+" odrive!")
                odv = odrive.find_any(serial_number=serial_number)
                atomic_print("refound " + name + " odrive")

    finally:
        atomic_print("Exiting and Sending safe command")
        send_state(odv, AXIS_STATE_IDLE)
        odv.axis0.controller.vel_setpoint = 0
        odv.axis1.controller.vel_setpoint = 0

if __name__ == "__main__":
    UDPLock = threading.Lock()
    threads = []
    tele = {}
    for odv in odrives:
        atomic_print("starting "+str(odv))
        thread = threading.Thread(target=run_odrive, args=odv, daemon=True)
        thread.start()
        threads.append(thread)

    # if any thread shuts down (which it shouldn't) we exit the program
    # which exits all other threads to 
    while all(t.is_alive() for t in threads):
        time.sleep(1)
        atomic_print(str(list( o[0] + str(t.is_alive()) for t,o in zip(threads,odrives))))
        telemetry.send(tele)
