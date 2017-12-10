# Interfacing FONA808 GSM/GPRS/GPS module
# GSM with Raspberry Pi 3 using Python
# Programmed By: Engr. Kier Musngi, CpE
# Last Updated: 12/10/2017 

import serial
from curses import ascii
import time

# Variables
recipient = "+639123456789""
message = "Hello World!"
modem = serial.Serial('/dev/serial0', 115200, timeout=1)

try:
    if modem.isOpen():
       modem.close()
    
    modem.open()
    modem.isOpen()

    print "Initializing GSM Text Mode"
    modem.write("AT+CMGF=1\r")
    time.sleep(1)

    print "Checking Network Signal"
    modem.write("AT+CSQ\r")
    time.sleep(3)

    print "Generating SMS Notification"
    modem.write('AT+CMGS="' + recipient.encode() + '\r')
    time.sleep(1)
    modem.write(message.encode() + "\r")
    time.sleep(1)
    modem.write(ascii.ctrl('z'))
    time.sleep(2)

    print "Message Sent!"

finally:
    modem.close()
