#!/usr/bin/python

import serial
from curses import ascii
import time

recipient = "+639123456789""
message = "Hello World!"
modem = serial.Serial('/dev/serial0', 115200, timeout=1)

try:
    if modem.isOpen():
       modem.close()
    
    modem.open()
    modem.isOpen()

    modem.write("AT+CMGF=1\r")
    time.sleep(1)
    print modem.readline()

    modem.write("AT+CSQ\r")
    time.sleep(3)
    print modem.readline()

    modem.write('AT+CMGS="' + recipient.encode() + '\r')
    time.sleep(1)
    modem.write(message.encode() + "\r")
    time.sleep(1)
    modem.write(ascii.ctrl('z'))
    time.sleep(2)

    print "Message Sent!"

finally:
    modem.close()
