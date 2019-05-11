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

middle_odrive = odrive.find_any(serial_number="206230804648")
print("found middle odrive")
front_odrive = odrive.find_any(serial_number="206C35733948")
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



front_odrive.axis0.controller.config.vel_gain = .15
front_odrive.axis1.controller.config.vel_gain = .15
    
middle_odrive.axis0.controller.config.vel_gain = .15
middle_odrive.axis1.controller.config.vel_gain = .15
    
back_odrive.axis0.controller.config.vel_gain = .15
back_odrive.axis1.controller.config.vel_gain = .15
    
#def explore
current_distribution = [.16,.16,.16,.16,.16,.16]
total_current = 80
control_mode_os = false
control_state = 1
prior_state = 1
stalled_motor = 6
stall_trip = 20

def get_data(front_odrive, middle_odrive, back_odrive):
    motor_currents[6]
    motor_currents[0] = front_odrive.axis0.motor.current_control.Iq_setpoint
    motor_currents[1] = front_odrive.axis1.motor.current_control.Iq_setpoint
    motor_currents[2] = middle_odrive.axis0.motor.current_control.Iq_setpoint
    motor_currents[3] = middle_odrive.axis1.motor.current_control.Iq_setpoint
    motor_currents[4] = back_odrive.axis0.motor.current_control.Iq_setpoint
    motor_currents[5] = back_odrive.axis1.motor.current_control.Iq_setpoint
    motor_vels[6]
    motor_currents[0] = front_odrive.axis0.encoder.vel_estimate
    motor_currents[1] = front_odrive.axis1.encoder.vel_estimate
    motor_currents[2] = middle_odrive.axis0.encoder.vel_estimate
    motor_currents[3] = middle_odrive.axis1.encoder.vel_estimate
    motor_currents[4] = back_odrive.axis0.encoder.vel_estimate
    motor_currents[5] = back_odrive.axis1.encoder.vel_estimate
    return motor_currents,motor_vels

while True:
    try:
        msg = cmd.get()
        print(msg)
        currents, vels = get_data(front_odrive,middle_odrive,back_odrive)
        try:
            telemetry.send( [middle_odrive.vbus_voltage] + currents )
        except:
            pass

        clear_errors(front_odrive)
        clear_errors(middle_odrive)
        clear_errors(back_odrive)

        if (msg['t'] == 0 and msg['f'] == 0):
            send_state(front_odrive, AXIS_STATE_IDLE)
            send_state(middle_odrive, AXIS_STATE_IDLE)
            send_state(back_odrive, AXIS_STATE_IDLE)
            control_mode_os = false
        else:
            if(!control_mode_os):
                front_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
                front_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
                middle_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
                middle_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
                back_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
                back_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
                control_mode_os = true
            
            if(control_state == 1):
                if(control_state != prior_state):
                    middle_odrive.axis0.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
                    middle_odrive.axis1.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
                    front_odrive.axis0.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
                    front_odrive.axis1.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
                    back_odrive.axis0.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
                    back_odrive.axis1.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
                    prior_state = control_state

                middle_odrive.axis0.controller.vel_setpoint = -150*(-msg['f'] - msg['t'])
                middle_odrive.axis1.controller.vel_setpoint = -150*(-msg['f'] + msg['t'])
                front_odrive.axis0.controller.vel_setpoint = -150*(msg['f'] + msg['t'])
                front_odrive.axis1.controller.vel_setpoint = 150*(msg['f'] - msg['t'])

                # back odrive is reversed left to right
                back_odrive.axis1.controller.vel_setpoint = 150*(msg['f'] - msg['t'])
                back_odrive.axis0.controller.vel_setpoint = -150*(msg['f'] + msg['t'])
                
                for i in Range(len(currents)):
                    if(currents[i] > stall_trip):
                        control_state = 2
                        stalled_motor = i
                        
                 if(msg['cur']):
                    control_state = 2
                
            elif(control_state == 2):
                if(control_state != prior_state):
                    middle_odrive.axis0.controller.config.control_mode = CTRL_MODE_CURRENT_CONTROL
                    middle_odrive.axis1.controller.config.control_mode = CTRL_MODE_CURRENT_CONTROL
                    front_odrive.axis0.controller.config.control_mode = CTRL_MODE_CURRENT_CONTROL
                    front_odrive.axis1.controller.config.control_mode = CTRL_MODE_CURRENT_CONTROL
                    back_odrive.axis0.controller.config.control_mode = CTRL_MODE_CURRENT_CONTROL
                    back_odrive.axis1.controller.config.control_mode = CTRL_MODE_CURRENT_CONTROL
                    prior_state = control_state

                if(msg['power_left']):
                    current_distribution = [.15,.03,.45,.03,.3,.03] 
                elif(msg['power_right']):
                    current_distribution = [.03,.15,.03,.45,.03,.3]
                elif(msg['power_mid']):
                    current_distribution = [.1,.1,.25,.25,.15,.15]
                elif(msg['power_back']):
                    current_distribution = [.125,.125,.125,.125,.25,.25]
                else:
                    current_distribution = [.16,.16,.16,.16,.16,.16]

                alloted_current = [total_current*temp for temp in current_distribution]

                if(abs(msg['f'])+abs(msg['t']) > 1):
                    scaling_factor = abs(msg['f'])+abs(msg['t'])
                    msg['f'] = msg['f']/scaling_factor
                    msg['t'] = msg['t']/scaling_factor
                    

                front_odrive.axis0.controller.current_setpoint = -alloted_current[0]*(-msg['f'] - msg['t'])
                front_odrive.axis1.controller.current_setpoint = alloted_current[1]*(-msg['f'] + msg['t'])
                middle_odrive.axis0.controller.current_setpoint = -alloted_current[2]*(msg['f'] + msg['t'])
                middle_odrive.axis1.controller.current_setpoint = -alloted_current[3]*(msg['f'] - msg['t'])

                # back odrive is reversed left to right
                back_odrive.axis1.controller.current_setpoint = -alloted_current[4]*(msg['f'] - msg['t'])
                back_odrive.axis0.controller.current_setpoint = alloted_current[5]*(msg['f'] + msg['t'])
                
                if(msg['vel']):
                    control_state = 1

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
        print("Shutting down")
        send_state(front_odrive, AXIS_STATE_IDLE)
        send_state(middle_odrive, AXIS_STATE_IDLE)
        send_state(back_odrive, AXIS_STATE_IDLE)
        middle_odrive.axis0.controller.vel_setpoint = 0
        middle_odrive.axis1.controller.vel_setpoint = 0
        front_odrive.axis0.controller.vel_setpoint = 0
        front_odrive.axis1.controller.vel_setpoint = 0
        back_odrive.axis0.controller.vel_setpoint = 0
        back_odrive.axis1.controller.vel_setpoint = 0
        raise
