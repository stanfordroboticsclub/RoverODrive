#!/usr/bin/env python3
import odrive
from odrive.enums import *
from fibre.protocol import ChannelBrokenException
from usb.core import USBError

from UDPComms import Subscriber, Publisher, timeout
import time

import os
import threading
import time


if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

cmd = Subscriber(8830, timeout = 0.3)
telemetry = Publisher(8810)

odrives = [ ['front' , "206C35733948", [-1, -1, 1, -1]],
            ['middle', "206230804648", [ 1,  1, 1, -1]],
            ['back'  , "207D35903948", [-1, -1, 1, -1]] ]

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
        return [odv.vbus_voltage,
                odv.axis0.motor.current_control.Iq_measured,
                odv.axis1.motor.current_control.Iq_measured]

def atomic_print(s):
    print(str(s)+'\n',end='')


def run_odrive(name, serial_number, d):
    # USBLock.acquire()
    atomic_print("looking for "+name+" odrive")
    odv = odrive.find_any(serial_number=serial_number)
    atomic_print("found " +name+ " odrive")
    send_state(odv, AXIS_STATE_IDLE)
    # USBLock.release()

    try:
        while True:
            # read from USB Block
            lostConnection = True
            try:
                UDPLock.acquire()
                atomic_print("Aqquired "+name)
                msg = cmd.get()
                atomic_print(msg)
                lostConnection = False
            except timeout:
                lostConnection = True
            finally:
                UDPLock.release()
                atomic_print("Relesed "+name)

            # Write to Odrives block
            try:
                clear_errors(odv)
                if lostConnection:
                    atomic_print("Timeout sending safe")
                    send_state(odv, AXIS_STATE_IDLE)
                else:
                    send_state(odv, AXIS_STATE_CLOSED_LOOP_CONTROL)
                    odv.axis0.controller.vel_setpoint =  d[0]*msg['f'] +d[1]*msg['t'] 
                    odv.axis1.controller.vel_setpoint =  d[2]*msg['f'] +d[3]*msg['t']
                    odv.axis0.watchdog_feed()
                    odv.axis1.watchdog_feed()

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
