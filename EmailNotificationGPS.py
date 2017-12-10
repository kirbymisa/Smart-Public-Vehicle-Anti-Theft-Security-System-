import time
import serial
import string
import pynmea2
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

#setting up mail information
fromaddr = "aics.thesis@gmail.com"
pword = "raspberrypi!@#$"
toaddr = "aics.thesis@gmail.com"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Location of the Vehicle"

#setup the serial port to which GPS is connected to
ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=0.5)

dataout  = pynmea2.NMEAStreamReader()

while True:
    newdata = ser.readline()
    print ("Getting new lat")
    if newdata[0:6] == '$GPGGA':
        newmsg = pynmea2.parse(newdata)
        newlat = newmsg.latitude
        print(newlat)
        newlong = newmsg.longitude
        print(newlong)
        lat  = str(newlat)
        lon = str(newlong)
        content = "http://maps.google.com/maps?q=" + lat + "," + lon
        Email = content
        msg.attach(MIMEText(Email, 'plain'))
        try:
	    server = smtplib.SMTP('smtp.gmail.com',587)
	    server.ehlo()
            server.starttls()
            server.login(fromaddr, pword)
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()
            print ("mail sent!")
        except:
            print("Error, Couldn't Send Mail, Be sure to enable non-secure apps login on sender's email")

        time.sleep(3)
