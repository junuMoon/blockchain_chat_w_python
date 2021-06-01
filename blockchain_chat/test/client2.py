import sys
import socket
import select

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 9009))

while 1:
    raw_msg = input()
    s.send(raw_msg.encode())
