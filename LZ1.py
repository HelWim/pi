#!/usr/bin/python3
# coding=utf-8
# Ulteaschallsensor
#Programm aus AZ-delivery e-book

# Levelmessung Zysterne

# Hochkomma daurch " ersetzt
# cd Helmut
# nohup python3 L3.py &
#sudo nano /etc/rc.local

# Display dazu gebaut





import time, datetime
import RPi.GPIO as GPIO
import csv, statistics
#from subprocess import call

'''
from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import sh1106

serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
'''
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
TRIG = 23  # BCM 4 funktioniert nicht gut, da er von der One-wire Schnittstelle auch benutzt werden kann
ECHO = 24
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, False)


F_Name="x"
Pfad="/home/pi/"


L1_werte=[]  #laufende Messungen
L1_60_werte=[] # Messungen der letzen 10min, rollierend
L1_alt=0
L1=0
distance1=0


def ultra1():
    global L1_werte, L1_alt, L1, L1_60_werte, distance1
    # grosser Ultraschallsensor
    print("ultra1")
    pulse_start=0
    pulse_end=0
    GPIO.output(TRIG, True)
    #time.sleep(0.00001)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    #print(datetime.datetime.now().strftime("%H:%M:%S"))
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    mt=time.time()+1 # maximal 1s auf den Impuls warten
    print("mt")
    while GPIO.input(ECHO) == 1 and time.time()<mt:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    
    if distance>300:
        distance=300
    distance1=("%.2f") % distance  
    L1_werte.append(distance)
    #L1=round(sum(L1_werte)/len(L1_werte),1)  
    L1=round(statistics.median(L1_werte),1)  
    print("L1",L1_werte,statistics.median(L1_werte))

    if len(L1_werte)>14:  # bei 2s Pause sind da 1/2 min Rolling average
        x=L1_werte.pop(0)
    L1_60_werte.append(L1)
    if len(L1_60_werte)>1800:  # auf 1h begrenzen
        x=L1_60_werte.pop(0)    

    print(L1_werte)
    #print (L1)
    #print(datetime.datetime.now().strftime("%H:%M:%S"),"Ultra1: Distance is {} cm".format(L1), "aktuell=",distance1)



time.sleep(2)
print("[press ctrl+c to end the script]")

F_Name=Pfad+str(datetime.date.today())+"_L.csv"    
file = open(F_Name, 'a') 
writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

writer.writerow([datetime.date.today(),datetime.datetime.now().strftime("%H:%M:%S"),   
    "0.11"]) 
Zeit_alt=time.time()
# display

'''
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 40), "Hello World", fill="white")
'''

time.sleep(1)

# Das ist aber ein rollierender Wert

try: # Main program loop
    while True:
        ultra1()
        time.sleep(2.01)

        if abs(L1-L1_alt) >=0.2:
            writer.writerow([datetime.date.today(),datetime.datetime.now().strftime("%H:%M:%S"),   
                L1])        
            L1_alt=L1

        '''
        anzeige1=str(datetime.date.today()) + " " + datetime.datetime.now().strftime("%H:%M:%S")
        anzeige2="30s MED "+str(L1)+"/"+str(L2)+"cm"
        #anzeige3="1h min/max " +str(min(L1_60_werte))+" "+str(max(L1_60_werte))
        anzeige3=str(min(L1_60_werte))+"/"+str(min(L2_60_werte))+"-"+str(max(L1_60_werte))+"/"+str(max(L2_60_werte))
        anzeige4="now "+str(distance1)+"/"+str(distance2)+"cm"
        #anzeige4="now "+str(distance2)+"cm "+str(GPIO.input(GPIO_AUS))
        #print (anzeige3)
        #print(GPIO.input(GPIO_AUS))


        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((5, 5), anzeige1, fill="white")  # x,y
            draw.text((5, 20), anzeige2, fill="white")  # x,y
            draw.text((5, 35), anzeige3, fill="white")  # x,y
            draw.text((5, 50), anzeige4, fill="white")  # x,y
            #file.flush()
        '''
        if F_Name != Pfad+str(datetime.date.today())+"_L.csv" or (time.time()-Zeit_alt)>600: #neuer Tag oder 10min vergangen = zwischenspeichern
            file.close()
            F_Name = Pfad+str(datetime.date.today())+"_L.csv"
            file = open(F_Name, 'a') 
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            Zeit_alt=time.time()
            # somit wird immer wenn das File regelmaessig geschlossen wird eine Zeile geschrieben
            # auch bei einem neuen File wird zu beginn eine Zeile geschrieben
            writer.writerow([datetime.date.today(),datetime.datetime.now().strftime("%H:%M:%S"),   
                L1])        
            L1_alt=L1
            

        
        
# Scavenging work after the end of the program
except KeyboardInterrupt:
    print("Script end!")
finally:
    print("schluss")
    writer.writerow([datetime.date.today(),datetime.datetime.now().strftime("%H:%M:%S"),   
        "0.99"]) 
    '''
    with canvas(device) as draw:
        draw.text((5, 20), "Finally", fill="white")  # x,y
    '''
    GPIO.cleanup()
    file.close()    
