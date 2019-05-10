#!/usr/bin/env python3

import odrive
from odrive.enums import *
import time
import sys

import os
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

reply = input("""This script will calibrate an odrive for use.
It will spin the motors as part of the process so make sure they are 
free to spin. If multiple odrives are connected it will calibrate a
random one so keep that in mind. You can calibrate a specific odrive by
supplying its hex serial number as the first argument

Do you want to proceed? [Y/n]""")


def find_odrive():
    if len(sys.argv) <= 1:
        return odrive.find_any()
    else:
        return odrive.find_any(serial_number=sys.argv[1])


if reply != "Y":
    print("Aborting...")
    exit()
else:
    print("Starting setup")

odrv0 = find_odrive()
print("Found ODrive", odrv0.serial_number)
time.sleep(1)


odrv0.erase_configuration()
odrv0.save_configuration()

time.sleep(2)
try:
    odrv0.reboot()
except:
    pass

odrv0 = find_odrive()
print("Found ODrive", odrv0.serial_number)
time.sleep(2)


ready = input("Ready to spin?")
if ready != "Y":
    print("Aborting...")
    exit()
else:
    print("Starting spin")

# this is important so the odrive knows it can't dump
# energy into the non existent brake resistor
#odrv0.erase_configuration() 

odrv0.config.brake_resistance = 0

# configure axis 0

odrv0.axis0.motor.config.pole_pairs = 15
odrv0.axis0.motor.config.resistance_calib_max_voltage = 4
odrv0.axis0.motor.config.requested_current_range = 25 #Requires config save and reboot
try:
    odrv0.axis0.motor.set_current_control_bandwidth(100)
except AttributeError:
    pass

odrv0.axis0.encoder.config.mode = 1
odrv0.axis0.encoder.config.cpr = 90

try:
    odrv0.axis0.encoder.config.bandwidth = 100
except AttributeError:
    pass
odrv0.axis0.controller.config.pos_gain = 1
odrv0.axis0.controller.config.vel_gain = 0.02
odrv0.axis0.controller.config.vel_integrator_gain = 0.1
odrv0.axis0.controller.config.vel_limit = 1000
odrv0.axis0.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL

# configure axis 1

odrv0.axis1.motor.config.pole_pairs = 15
odrv0.axis1.motor.config.resistance_calib_max_voltage = 4
odrv0.axis1.motor.config.requested_current_range = 25 #Requires config save and reboot
try:
    odrv0.axis1.motor.set_current_control_bandwidth(100)
except AttributeError:
    pass

odrv0.axis1.encoder.config.mode = 1
odrv0.axis1.encoder.config.cpr = 90

try:
    odrv0.axis1.encoder.config.bandwidth = 100
except AttributeError:
    pass
odrv0.axis1.controller.config.pos_gain = 1
odrv0.axis1.controller.config.vel_gain = 0.02
odrv0.axis1.controller.config.vel_integrator_gain = 0.1
odrv0.axis1.controller.config.vel_limit = 1000
odrv0.axis1.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL


# axis 0
print("Motor 0")
odrv0.axis0.requested_state = AXIS_STATE_MOTOR_CALIBRATION
time.sleep(10)
assert odrv0.axis0.motor.error == 0, odrv0.axis0.motor.error
odrv0.axis0.motor.config.pre_calibrated = True

print("Encoder 0")
odrv0.axis0.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
time.sleep(10)
assert odrv0.axis0.encoder.error == 0, odrv0.axis0.encoder.error
odrv0.axis0.encoder.config.pre_calibrated = True

# axis 1
print("Motor 1")
odrv0.axis1.requested_state = AXIS_STATE_MOTOR_CALIBRATION
time.sleep(10)
assert odrv0.axis1.motor.error == 0, odrv0.axis1.motor.error
odrv0.axis1.motor.config.pre_calibrated = True

print("Encoder 1")
odrv0.axis1.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
time.sleep(10)
assert odrv0.axis1.encoder.error == 0, odrv0.axis1.encoder.error
odrv0.axis1.encoder.config.pre_calibrated = True

# still looking for good values
odrv0.axis0.motor.config.current_lim = 25
odrv0.axis1.motor.config.current_lim = 25

odrv0.save_configuration()

time.sleep(3)
try:
    odrv0.reboot()
except:
    pass

print("Done!")
exit()

def drive(odrive, speed):
     odrive.axis1.controller.vel_setpoint = speed
     odrive.axis0.controller.vel_setpoint = -speed

def off(odrive):
     odrive.axis1.requested_state = AXIS_STATE_IDLE
     odrive.axis0.requested_state = AXIS_STATE_IDLE

def on(odrive):
     odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
     odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

