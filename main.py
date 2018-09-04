#!/usr/bin/env python3
import socket
import struct
#import odrive

UDP_IP = ""
UDP_PORT = 6001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
socket.settimeout(2)

s = struct.Struct('ff')

try:
    while True:
        data, addr = sock.recvfrom(1024)
        left,right = s.unpack(data)
        print(left,right)
        # odrv0.axis0.controller.vel_setpoint = left
        # odrv0.axis1.controller.vel_setpoint = right
except:
    raise
    # odrv0.axis0.controller.vel_setpoint = 0
    # odrv0.axis1.controller.vel_setpoint = 0

