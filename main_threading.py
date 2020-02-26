#!/usr/bin/env python3
import odrive
from odrive.utils import dump_errors
from odrive.enums import *
from fibre.protocol import ChannelBrokenException
from usb.core import USBError

from UDPComms import Subscriber, Publisher, timeout

import os
import threading
import time
import io
from contextlib import redirect_stdout


if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

cmd = Subscriber(8830, timeout = 0.3)
telemetry = Publisher(8810)

# motor 0 is right
# motor 1 is left
odrives = [ ['middle', "208D358D524B", [-1, 1]],
            ['front' , "2092358D524B", [-1, 1]],
            ['back'  , "2092357A524B", [-1, 1]]]

def clear_errors(name, odv):
    if odv.axis0.error or odv.axis1.error:
        with PrintLock:
            print("Errors on", name)
            dump_errors(odv, True)

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
                clear_errors(name, odv)
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
    UDPLock   = threading.Lock()
    PrintLock = threading.Lock()
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
