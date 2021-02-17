#!/usr/bin/python3
# coding=utf-8
# Auslesen des Stromsensor für die FWM Umlaufpumpe
# Import required Python libraries
import time
import Adafruit_ADS1x15
adc1 = Adafruit_ADS1x15.ADS1115(address=0x48) # Create an ADS1115 ADC (16-bit) 
adc2 = Adafruit_ADS1x15.ADS1115(address=0x49) # Create an ADS1115 ADC (16-bit) 
GAIN = 1
strom1=[1,2,3]
strom2=[1,2,3]
grenze=60 # Grenzwert bei dem die Pumpe EIN ist
z=0
zustand='AUS'
print('[press ctrl+c to end the script]') 
try: # Main program loop
    while True:
        strom1[z] = adc1.read_adc(0, gain=GAIN) # Read the ADC channel 0 value - Strom invasiv
        strom2[z] = adc1.read_adc(1, gain=GAIN) # Read the ADC channel 1 value - Strom nicht invasiv
        z=z+1
        if z>2:
            z=0
        mittel1=sum(strom1)/len(strom1)
        diff1=max(strom1)-min(strom1)
        mittel2=sum(strom2)/len(strom2)
        if diff1>grenze:
            zustand='EIN'
        else:
            zustand='AUS'
        print (strom1, "-","Av=%6.0f" % mittel1,"- Min=%6.0f" % min(strom1),
        "- Max=%6.0f" % max(strom1), "- D=%6.0f" % (max(strom1)-min(strom1)), "-",zustand)
        print (strom2, "-","Av=%6.0f" % mittel2,"- Min=%6.0f" % min(strom2),
        "- Max=%6.0f" % max(strom2), "- D=%6.0f" % (max(strom2)-min(strom2)), "-",zustand)
        print("----")
        time.sleep(1.5)
# Scavenging work after the end of the program
except KeyboardInterrupt:
    print('Script end!')
