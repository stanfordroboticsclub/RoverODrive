# RoverODrive
Uses an RPi as a bridge between udp messages and serial sent to an [ODrive](https://odriverobotics.com)

Prerequisites
----
- Make sure you have the [UDPComms](https://github.com/stanfordroboticsclub/UDPComms) library installed before using


Usage
----
- `sudo python3 main.py`


Files
------

`main.py` - Drives 3 ODrives based on commands published on port 8830. Also publishes telemetry
`single.py` - Drives a single ODrive based on commands published on port 8830 
`odrive_setup.y` - Sets up an fresh ODrive to be used with the Hub motors
