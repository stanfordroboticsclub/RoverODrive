import socket
import struct
import time

speed = 100

UDP_IP = "10.0.0.11"
UDP_PORT = 6001

# print "UDP target IP:", UDP_IP
# print "UDP target port:", UDP_PORT
# print "message:", MESSAGE

s = struct.Struct('ff')

last_char=" "

while True:
    MESSAGE = s.pack(speed,speed)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    time.sleep(1)


