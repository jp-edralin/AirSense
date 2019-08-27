#importing libraries
import os
import glob
import time
import grovepi
import math
from gps import *
import threading
import serial
import RPi.GPIO as GPIO
#Output file name
file_name = "/home/pi/Desktop/Files/{}_TempData.txt".format(time.strftime("%H-%M-%S_%m-%d-%Y"))

#-------------------------------sensor setup and intialization
#LED and Switch
GPIO.setmode(GPIO.BCM)
GPIO.setup(10,GPIO.OUT)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPS
gpsd = None #seting the global variable

os.system('clear') #clear the terminal (optional)

class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd #bring it in scope
        gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.current_value = None
        self.running = True #setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
            gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

gpsp = GpsPoller() # create the thread
gpsp.start() # start it up

#Air Quality
# Connect the Grove Air Quality Sensor to analog port A0
# SIG,NC,VCC,GND
air_sensor = 0

grovepi.pinMode(air_sensor,"INPUT")

ser = serial.Serial('/dev/ttyACM0',9600, timeout=0.5)
s = [0]

#--------------------------------Code Body

f = open(file_name, "w")
f.write("Time,Temperature,Humidity,Quality Score,PM10 count,PM2.5 count,PM10 conc,PM2.5 conc,Lat,Long,Alt,Speed,Climb{}".format("\n"))
f.write("------------------------------------------------------------------------------------------------------------\n")
f.close()
TurnOff = False
while True:
    while (GPIO.input(22)==True):
        GPIO.output(10,1)
        Time = time.strftime("%H:%M:%S %m/%d/%Y", time.localtime())
        [Temperature,Humidity] = grovepi.dht(3,1)
        QualityScore = grovepi.analogRead(air_sensor)
        PM = ""
        while(len(PM)<2):
            PM=ser.readline()
            PM =  PM.strip()
        Lat = gpsd.fix.latitude
        Long = gpsd.fix.longitude
        Alt = gpsd.fix.altitude
        Speed = gpsd.fix.speed
        Climb = gpsd.fix.climb
        TurnOff = True
        print("{},{},{},{},{},{},{},{},{},{}{}".format(Time, Temperature, Humidity, QualityScore, PM, Lat, Long, Alt, Speed, Climb,"\n"))
        f = open(file_name, "a")
        f.write("{},{},{},{},{},{},{},{},{},{}{}".format(Time, Temperature, Humidity, QualityScore, PM, Lat, Long, Alt, Speed, Climb,"\n"))
        f.close()
        #except(KeyboardInterrupt, SystemExit): #when you press ctrl+c
    while(GPIO.input(22)==False):
        if(TurnOff == True):
            #print ("\nKilling...")
            GPIO.output(10,0)
            gpsp.running = False
            gpsp.join() # wait for the thread to finish what it's doing
            f.close()
            print ("Done.\nExiting.")
            TurnOff = False
    #break
