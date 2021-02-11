#!/usr/bin/python3
# coding=utf-8
# Auslesen des Drucksensors des Heizungswassers
# 5V=32752 am A/D,  4.5V=29477 am A/D
# 4.5V = 5.52barg = 29477 Ausgang am A/D Wandler
# 1bar =5340
# Gemessen 0bar ..3936, 4bar..26608
# Import required Python libraries
import time
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115() # Create an ADS1115 ADC (16-bit) instance
GAIN = 1
z=0
values=[1,2,3]
print('[press ctrl+c to end the script]') 
try: # Main program loop
    

    while True:
        
        values[z] = adc.read_adc(1, gain=GAIN) # Read the ADC channel 1 value
        z=z+1
        if z>2:
            z=0
        mittel=sum(values)/len(values)
        druck=(mittel-3936)/(26608-3936)*4
        #print('{0:>6}'.format(mittel), " %6.2f barg" % druck,)
        print(" %6.2f barg" % druck)
        time.sleep(2)
# Scavenging work after the end of the program
except KeyboardInterrupt:
    print('Script end!')
