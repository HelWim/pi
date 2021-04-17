#!/usr/bin/python3
# coding=utf-8
# Auslesen von 2 D/A Wandlern
import Adafruit_ADS1x15
import time
adc1 = Adafruit_ADS1x15.ADS1115(address=0x48) # Create an ADS1115 ADC (16-bit) 
adc2 = Adafruit_ADS1x15.ADS1115(address=0x49) # Create an ADS1115 ADC (16-bit) 
GAIN = 1
print(adc1.read_adc(0, gain=GAIN)) # Read the ADC channel 0 value
print(adc1.read_adc(1, gain=GAIN)) # Read the ADC channel 1 value
print(adc1.read_adc(2, gain=GAIN)) # Read the ADC channel 2 value
print(adc1.read_adc(3, gain=GAIN)) # Read the ADC channel 3 value

# Nur aktivieren wenn wirklich zweiter A/D wandler angeschlossen ist
"""
print(adc2.read_adc(0, gain=GAIN)) # Read the ADC channel 0 value
print(adc2.read_adc(1, gain=GAIN)) # Read the ADC channel 1 value
print(adc2.read_adc(2, gain=GAIN)) # Read the ADC channel 2 value
print(adc2.read_adc(3, gain=GAIN)) # Read the ADC channel 3 value
"""

try: # Main program loop
    while True:
        roh=adc1.read_adc(2, gain=GAIN)
        druck=(roh-3936)/(24834-3936)*4
        print(druck)
        #print("adc1-Kanal2 ",adc1.read_adc(1, gain=GAIN))
        time.sleep(0.5)

except KeyboardInterrupt:
    print('Script end!')        
