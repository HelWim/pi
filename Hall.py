#!/usr/bin/python3
# coding=utf-8
# Auslesen des Hallsensor und Hall Mini
# ADC Channes:
#               0 .. Strom
#               1 .. Druck
#               2 .. Hall

import Adafruit_ADS1x15
import time
import RPi.GPIO as GPIO

# We will be using the BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Select a control GPIO
GPIO_HALL = 26
GPIO_HALL_MINI = 16

# Set CONTROL to INPUT mode
GPIO.setup(GPIO_HALL, GPIO.IN)
GPIO.setup(GPIO_HALL_MINI, GPIO.IN)


adc = Adafruit_ADS1x15.ADS1115() # Create an ADS1115 ADC (16-bit) instance
GAIN = 1


print('[press ctrl+c to end the script]') 
try: # Main program loop
    while True:
        values = adc.read_adc(2, gain=GAIN) # Read the ADC channel 2 value    
        print ("Hall-Analog=%6.0f" % values, "HALL-DI:",GPIO.input(GPIO_HALL), "HALLmini-DI:",GPIO.input(GPIO_HALL_MINI))
        time.sleep(0.5)

# Scavenging work after the end of the program
except KeyboardInterrupt:
    print('Script end!')
    GPIO.cleanup()
