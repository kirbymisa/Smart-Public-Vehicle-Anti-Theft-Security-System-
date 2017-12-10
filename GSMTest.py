#!/usr/bin/python
import serial
from curses import ascii
import time

recipient = "+639272548944"
message = "Sapnu puas"
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
time.sleep(1)
print modem.readline()

modem.write('AT+CMGS="' + recipient.encode() + '"\r')

modem.write(message.encode() + "\r")
modem.write(ascii.ctrl('z'))

time.sleep(2)
print modem.readlines()

finally:
    modem.close()
