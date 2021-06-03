#!/usr/bin/python3
# coding=utf-8
# Import required Python libraries
#schaltet das 4. Relais um Kessel zu aktivieren
import RPi.GPIO as GPIO
import time

# We will be using the BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Select a control GPIO
GPIO_CONTROL = 16 #Pin36

# Set CONTROL to OUTPUT mode
GPIO.setup(GPIO_CONTROL, GPIO.OUT)

# Main function
def main():

  try:
    # Repeat till the program is ended by the user
    while True:

      spanne=5 #alle x s wird eine Meldung
      print('Ist EIN -',time.asctime())    
      GPIO.output(GPIO_CONTROL, False)
      time.sleep(spanne)

  # If the program is ended cleanup GPIOs
  except KeyboardInterrupt:
    #GPIO.cleanup()
    GPIO.output(GPIO_CONTROL, True) #Reslais wieder absteuern

# Run the main function when the script is executed
if __name__ == "__main__":
    main()