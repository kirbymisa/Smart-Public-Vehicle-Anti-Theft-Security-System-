import serial
import subprocess
import json
import urllib2
import os
import datetime
import time
import pyrebase
import RPi.GPIO as GPIO
from subprocess import CalledProcessError
from picamera import PiCamera
from threading import Thread
from firebase import firebase
from curses import ascii
from time import sleep

#Firebase pyrebase library configurations
pyreConfig = {
    "apiKey": "AIzaSyCSZV_mIb5joS5OVNM8Rd8islEA2Ij6-c0",
    "authDomain": "vehiclegpstrackingapp.firebaseapp.com",
    "databaseURL": "https://vehiclegpstrackingapp.firebaseio.com",
    "storageBucket": "vehiclegpstrackingapp.appspot.com",
    "serviceAccount": "/home/pi/Storage/VehicleGPSTrackingApp-7c42fa645218.json"
}

#Pin configuration
ledOrange = 23 # Led indicator for stabilizing fix
ledYellow = 24 # Led indicator for internet status
ledBlue = 22 # Led indicator for sending 10 seconds video
buttonSource = 20 # Source for Emergency Button Interrupt
rfButton = 17 # Input of RF Transmitter
interruptButton = 21 # Input interrupt

# GPIO pin setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledOrange, GPIO.OUT)
GPIO.setup(ledYellow, GPIO.OUT)
GPIO.setup(ledBlue, GPIO.OUT)
GPIO.setup(rfButton, GPIO.IN)
GPIO.setup(interruptButton, GPIO.IN)
GPIO.setup(buttonSource, GPIO.OUT)
GPIO.output(buttonSource, GPIO.HIGH)

# Camera setup
camera = PiCamera()
camera.exposure_mode = 'antishake'
camera.rotation = 180

# Instantiate serial connection
serialCon = serial.Serial('/dev/serial0', 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

# Instantiate firebase connection
firebaseCon = firebase.FirebaseApplication('https://vehiclegpstrackingapp.firebaseio.com/', None)

# Default variables, used when there is no or unstable internet connection
# Default contact number: Police Head Office
# Default vehicle information:
defaultNumber = '+639773839745"'
defaultVehicleType = "Bus"
defaultVehicleColor = "White"
defaultPlateNumber = "DTF304"
defaultDriverName = "Rogelio Alvarez"

# Function definitions:
def InternetIsAvailable():
    try:
        urllib2.urlopen('https://www.google.com.ph/', timeout=1)
        return True
    except urllib2.URLError as err: 
        return False

def ActivateGPS():
    try:
        if serialCon.isOpen():
           serialCon.close()
        serialCon.open()
        serialCon.isOpen()

        print "Activating GPS"
        print "Please wait for a moment ..."
        serialCon.write("AT+CGNSPWR=1\r")
        serialCon.write("AT+CGNSPWR?\r")
        print "Checking GPS power status ..."
        gpsIsNotActivated = True
        while gpsIsNotActivated:
            response = serialCon.readline()
            if "+CGNSPWR: 1" in response:
                print "GPS Power Status: ON"
                break
        print "GPS activated."
    finally:
        serialCon.close()

def FindGPSFix():
    try:
        if serialCon.isOpen():
           serialCon.close()
        serialCon.open()
        serialCon.isOpen()

        print "Checking for GPS fix ..."
        print "Please wait while GPS is trying to find a fix."  
        gpsHasNoFix = True
        while gpsHasNoFix:  
            serialCon.write("AT+CGNSINF\r")
            response = serialCon.readline()  
            if "+CGNSINF: 1,1," in response:
                print "GPS successfully found a fix."
                break 
    finally:
        serialCon.close()

def GetLatitude():
    try:
        if serialCon.isOpen():
           serialCon.close()
        serialCon.open()
        serialCon.isOpen()

        print "Parsing GPS NMEA Code ..."
        print "Fetching Coordinates ..."
        print "Getting Latitude ..."
        serialCon.write("AT+CGNSINF\r")
        isNoLatitude = True
        while isNoLatitude:
            response = serialCon.readline()
            if "+CGNSINF: 1" in response:
                valueStream = response.split(":")
                break
        value = valueStream[1]
        dataStream = value.split(",")
        latitude = dataStream[3]
        print "Latitude: " + latitude
        return latitude
    finally:
        serialCon.close()   

def GetLongitude():
    try:
        if serialCon.isOpen():
           serialCon.close()
        serialCon.open()
        serialCon.isOpen()

        print "Getting Longitude ..."
        serialCon.write("AT+CGNSINF\r")
        isNoLongitude = True
        while isNoLongitude:
            response = serialCon.readline()
            if "+CGNSINF: 1" in response:
                valueStream = response.split(":")
                break
        value = valueStream[1]
        dataStream = value.split(",")
        longitude = dataStream[4]
        print "Longitude: " + longitude
        return longitude
    finally:
        serialCon.close() 

def ActivateGSM():
    try:
        if serialCon.isOpen():
           serialCon.close()
        serialCon.open()
        serialCon.isOpen()

        print "Activating GSM ..."
        print "Initializing GSM to text mode ..."
        serialCon.write("AT+CMGF=1\r")
        sleep(1)
        print "GSM text mode activated."
    finally:
        serialCon.close()

def GetCoordinates():
    try:
        if serialCon.isOpen():
           serialCon.close()
        serialCon.open()
        serialCon.isOpen()
        
        rawlatitude = GetLatitude()
        rawlongitude = GetLongitude()
        lat = str(rawlatitude)
        lon = str(rawlongitude)
        return lat + "," + lon
    finally:
        serialCon.close()

def SendEmergencySMS(vMobileNumber, vType, vColor, vPlateNumber, vDriverName, vCoordinates):
    try:
        if serialCon.isOpen():
           serialCon.close()
        serialCon.open()
        serialCon.isOpen()

        print "Composing Emergency Alert Message ..."
        serialCon.write('AT+CMGS="' + vMobileNumber + '\r')
        sleep(0.5)
        serialCon.write('SMART VEHICLE EMERGENCY ALERT!\r')
        sleep(0.5)
        serialCon.write('Vehicle Type: ' + vType + '\r')
        sleep(0.5)
        serialCon.write('Vehicle Color: ' + vColor + '\r')
        sleep(0.5)
        serialCon.write('Plate Number: ' + vPlateNumber + '\r')
        sleep(0.5)
        serialCon.write('Driver Name: ' + vDriverName + '\r')
        sleep(0.5)
        serialCon.write('Last location located: https://www.google.com/maps/place/' + vCoordinates + '\r')
        sleep(0.5)
        serialCon.write(ascii.ctrl('z'))

        waitingMessageToBeSent = True
        while waitingMessageToBeSent:
            response = serialCon.readline()
            if "+CMGS: " in response:
                print "Message sent!"
                break
            if "ERROR" in response:
                print "Sending Failed"
                break
    finally:
        serialCon.close()

def GenerateVideoFilePath(videoFileName):
    return '/home/pi/Documents/Video/' + videoFileName

def GenerateVideoFileName():
    return datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S') + '.h264'

def RecordTenSecondsVideo(videoFilePath):
    camera.start_recording(videoFilePath)
    sleep(11)
    camera.stop_recording()

def SendTenSecondsVideoToFireBase(videoFileName, videoFilePath):
    GPIO.output(ledBlue, GPIO.HIGH)
    pyreCon = pyrebase.initialize_app(pyreConfig)
    pyreStorage = pyreCon.storage()
    mp4FileName = os.path.splitext(videoFileName)[0] + ".mp4"
    mp4FilePath = os.path.splitext(videoFilePath)[0] + ".mp4"
    pyreStorage.child("Videos/" + mp4FileName).put(mp4FilePath)
    print "Video successfully sent!"
    parentName = os.path.splitext(videoFileName)[0]
    firebaseCon.put('VideoInfo', parentName, {'FileName':mp4FileName})
    firebaseCon.put('RecentVideoInfo', 'FileName', mp4FileName)

def RFEmergencyButtonIsTriggered():
    if GPIO.input(17)==False:
        return True
    else:
        return False

def ManualEmergencyButtonInterruptIsTriggered():
    if GPIO.input(21):
        return True
    else:
        return False

def SendCoordinatesToFirebase():
    coordinates = GetCoordinates()
    firebaseCon.put('VehicleGPS', 'RealTimeLocation', coordinates)

def ConvertVideoToMP4(videoFilePath):
    cmd = "MP4Box -add {} {}.mp4".format(videoFilePath, os.path.splitext(videoFilePath)[0])
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print "Failed to convert video"

def CheckFIx():
    try:
        if serialCon.isOpen():
           serialCon.close()
        serialCon.open()
        serialCon.isOpen()

        serialCon.write("AT+CGNSINF\r")
        replyIsNotValid = True
        while replyIsNotValid:
            response = serialCon.readline() 
            if "+CGNSINF:" in response:
                if "+CGNSINF: 1,1" in response:
                    print "GPS fix Status: True"
                    replyIsNotValid = False
                    return True
                else:
                    print "GPS Fix Status: False"
                    print "Returning current fix data"
                    replyIsNotValid = False
                    return False
    finally:
        serialCon.close()

def SendSMSEvery5Seconds():
    while True:
        if CheckFIx(): 
            latlon = GetCoordinates()
            SendEmergencySMS(defaultNumber, defaultVehicleType, defaultVehicleColor, defaultPlateNumber, defaultDriverName, latlon)
            sleep(5)
        else: 
            SendEmergencySMS(defaultNumber, defaultVehicleType, defaultVehicleColor, defaultPlateNumber, defaultDriverName, 'No Fix')
            sleep(5)

def CheckUnsent():
    try:
        if serialCon.isOpen():
           serialCon.close()
        serialCon.open()
        serialCon.isOpen()

        serialCon.write(ascii.ctrl('z'))
        sleep(5)
        print "Cleared unsent messages"
        
    finally:
        serialCon.close()

def Reboot():
    cmd = "sudo reboot now"
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print "Failed to reboot raspberry pi"

#-----------------------------------------------------------------------------------------------------------------------------------------------
# Main Code Logic:
# (Main Algorithm)
try:
    CheckUnsent()
    ActivateGPS()
    ActivateGSM()
    FindGPSFix()
    GPIO.output(ledOrange, GPIO.HIGH)
    primaryVideoName = GenerateVideoFileName()
    primaryVideoPath = GenerateVideoFilePath(primaryVideoName)
    camera.start_recording(primaryVideoPath)

    print "Waiting for an Emergency"
    rfIsNotTriggered = True
    while rfIsNotTriggered:
        if RFEmergencyButtonIsTriggered():
            break

    rfIsTriggered = True   
    if rfIsTriggered:
        GPIO.output(ledYellow, GPIO.HIGH)
        mCoordinates = GetCoordinates()

        if InternetIsAvailable():
            # Cloud variables: Data gathered from Firebase (Cloud Database)
            # Contact numbers:
            policeNumbers = firebaseCon.get('PoliceContact', None)
            contactLists = [str(policeNumbers['PoliceA']), str(policeNumbers['PoliceB']), str(policeNumbers['PoliceC'])]
            # Vehicle information:
            vehicleInfo = firebaseCon.get('VehicleInfo', None)
            vehicleType = str(vehicleInfo['VehicleType'])
            vehicleColor = str(vehicleInfo['VehicleColor']) 
            plateNumber = str(vehicleInfo['PlateNumber'])
            driverName = str(vehicleInfo['DriverName'])
            camera.stop_recording()

            print "Network Available!"
            
            firebaseCon.put('InterruptEmergency', 'EmergencyStatus', 1)
            print "Emergency status set to 1"

            videoNameToBeSend = GenerateVideoFileName()
            videoPathToBeSend = GenerateVideoFilePath(videoNameToBeSend)
            RecordTenSecondsVideo(videoPathToBeSend)
            print "Converting Video to Mp4"
            ConvertVideoToMP4(videoPathToBeSend)
            Thread1 = Thread(target=SendTenSecondsVideoToFireBase, args=(videoNameToBeSend, videoPathToBeSend,))
            print "Sending Video to Firebase"
            Thread1.start()

            secondaryVideoName = GenerateVideoFileName()
            secondaryVideoPath = GenerateVideoFilePath(secondaryVideoName)
            camera.start_recording(secondaryVideoPath)

            for vContact in contactLists:
                SendEmergencySMS(vContact, vehicleType, vehicleColor, plateNumber, driverName, mCoordinates)
            
            firebaseCon.put('VehicleInfo','LastLocated', mCoordinates)

            emergencyIsOn = True

            while emergencyIsOn:
                isFixed = CheckFIx()
                firebaseCon.put('GPSButton','GPSStatus', 1)
                if isFixed: 
                    SendCoordinatesToFirebase() 
                    sleep(0.5)
                    emergencyCurrentStatus = firebaseCon.get('InterruptEmergency', 'EmergencyStatus')
                else: 
                    currentLocation = firebaseCon.get('VehicleGPS', 'RealTimeLocation')
                    firebaseCon.put('VehicleGPS','RealTimeLocation', currentLocation)
                    sleep(0.5)
                    emergencyCurrentStatus = firebaseCon.get('InterruptEmergency', 'EmergencyStatus')

                if ManualEmergencyButtonInterruptIsTriggered() or emergencyCurrentStatus == 0:
                    break
            camera.stop_recording()
            print "Emergency Terminated"
        else:
            print "No Network Found!"
            print "Initializing Offline Mode."

            Thread2 = Thread(target=SendSMSEvery5Seconds)
            Thread2.start()

            emergencyIsOn = True
            while emergencyIsOn:
                if ManualEmergencyButtonInterruptIsTriggered():
                    break
            camera.stop_recording()
            print "Emergency Terminated"

finally:
    if InternetIsAvailable():
        firebaseCon.put('GPSButton', 'GPSStatus', 0)
        firebaseCon.put('InterruptEmergency', 'EmergencyStatus', 0)
    if serialCon.isOpen():
        serialCon.close()
    GPIO.output(ledYellow, GPIO.LOW)
    GPIO.output(ledYellow, GPIO.LOW)
    GPIO.output(ledYellow, GPIO.LOW)  
    GPIO.cleanup()
    Reboot()
