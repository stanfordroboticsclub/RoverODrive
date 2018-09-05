
odrv0.axis0.motor.config.pole_pairs = 15
odrv0.axis0.motor.config.resistance_calib_max_voltage = 4
odrv0.axis0.motor.config.requested_current_range = 25 #Requires config save and reboot
odrv0.axis0.motor.set_current_control_bandwidth(100)

odrv0.axis0.encoder.config.mode = 1
odrv0.axis0.encoder.config.cpr = 90

odrv0.axis0.encoder.config.bandwidth = 100
odrv0.axis0.controller.config.pos_gain = 1
odrv0.axis0.controller.config.vel_gain = 0.02
odrv0.axis0.controller.config.vel_integrator_gain = 0.1
odrv0.axis0.controller.config.vel_limit = 1000
odrv0.axis0.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL



odrv0.axis1.motor.config.pole_pairs = 15
odrv0.axis1.motor.config.resistance_calib_max_voltage = 4
odrv0.axis1.motor.config.requested_current_range = 25 #Requires config save and reboot
odrv0.axis1.motor.set_current_control_bandwidth(100)

odrv0.axis1.encoder.config.mode = 1
odrv0.axis1.encoder.config.cpr = 90

odrv0.axis1.encoder.config.bandwidth = 100
odrv0.axis1.controller.config.pos_gain = 1
odrv0.axis1.controller.config.vel_gain = 0.02
odrv0.axis1.controller.config.vel_integrator_gain = 0.1
odrv0.axis1.controller.config.vel_limit = 1000
odrv0.axis1.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL


odrv0.save_configuration()
odrv0.reboot()


odrv0.axis0.requested_state = AXIS_STATE_MOTOR_CALIBRATION
odrv0.axis0.motor
odrv0.axis0.motor.config.pre_calibrated = True

odrv0.axis0.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
odrv0.axis0.encoder
odrv0.axis0.encoder.config.pre_calibrated = True

odrv0.axis1.requested_state = AXIS_STATE_MOTOR_CALIBRATION
odrv0.axis1.motor
odrv0.axis1.motor.config.pre_calibrated = True

odrv0.axis1.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
odrv0.axis1.encoder
odrv0.axis1.encoder.config.pre_calibrated = True

odrv0.save_configuration()
odrv0.reboot()


odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
odrv0.axis0.controller.vel_setpoint = 120


def drive(odrive, speed):
     odrive.axis1.controller.vel_setpoint = speed
     odrive.axis0.controller.vel_setpoint = -speed

def off(odrive):
     odrive.axis1.requested_state = AXIS_STATE_IDLE
     odrive.axis0.requested_state = AXIS_STATE_IDLE

def on(odrive):
     odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
     odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL



pi@raspberrypi:~$ sudo odrivetool --path serial:/dev/ttyS0 --verbose
ODrive control utility v0.4.2
Waiting for ODrive...
Connecting to device on serial port /dev/ttyS0@115200
Please connect your ODrive.
You can also type help() or quit().

In [1]:

no response - probably incompatible
In [1]:
