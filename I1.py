#!/usr/bin/python3
# coding=utf-8
# Auslesen des Stromsensor für die FWM Umlaufpumpe
# Import required Python libraries
import time
import Adafruit_ADS1x15
adc = Adafruit_ADS1x15.ADS1115() # Create an ADS1115 ADC (16-bit) instance
GAIN = 1
strom=[1,2,3]
grenze=21500 # Grenzwert bei dem die Pumpe EIN ist
z=0
zustand='AUS'
print('[press ctrl+c to end the script]') 
try: # Main program loop
    while True:
        strom[z] = adc.read_adc(0, gain=GAIN) # Read the ADC channel 0 value
        z=z+1
        if z>2:
            z=0
        mittel=sum(strom)/len(strom)
        if max(strom)>grenze:
            zustand='EIN'
        else:
            zustand='AUS'
        print (strom, "-","Av=%6.0f" % mittel,"- Min=%6.0f" % min(strom),
        "- Max=%6.0f" % max(strom), "- D=%6.0f" % (max(strom)-min(strom)), "-",zustand)
       # print("%6.0f" % mittel,"Max= %6.0f" % max(durch) )
       # print("Max= %6.0f" % max(durch))
        time.sleep(0.5)
# Scavenging work after the end of the program
except KeyboardInterrupt:
    print('Script end!')
