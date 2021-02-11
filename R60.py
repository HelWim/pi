#!/usr/bin/python3
# coding=utf-8
# Import required Python libraries
import RPi.GPIO as GPIO
import time

# We will be using the BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Select a control GPIO
GPIO_CONTROL = 17

# Set CONTROL to OUTPUT mode
GPIO.setup(GPIO_CONTROL, GPIO.OUT)

# Main function
def main():

  try:
    # Repeat till the program is ended by the user
    while True:
      dauer=60 #Dauer der Warmwasserbereitstellung
      spanne=5 #alle x s wird eine Meldung über verbleibende Zeit
      print('Ist EIN -',time.asctime())    
      GPIO.output(GPIO_CONTROL, False)
      while dauer>0:
        print('noch',dauer,'s.')
        time.sleep(spanne)
        dauer=dauer-spanne
      GPIO.output(GPIO_CONTROL, True)
      print('Ist AUS -',time.asctime())      
      # Wait while ENTER is pressed
      was=input('Drücke Enter')
  # If the program is ended cleanup GPIOs
  except KeyboardInterrupt:
    GPIO.cleanup()

# Run the main function when the script is executed
if __name__ == "__main__":
    main()