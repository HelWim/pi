#!/usr/bin/env python3
# coding=utf-8
# Umstellen auf AZ-delviery Temperaturauslesen

import RPi.GPIO as GPIO
import os, time, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import Adafruit_ADS1x15
import math
from DS18B20classFile import DS18B20
import csv

adc = Adafruit_ADS1x15.ADS1115() # Create an ADS1115 ADC (16-bit) instance

host_name = '192.168.178.40'  # IP Address of Raspberry Pi
host_port = 8000
Pumpe_Status="AUS"
P_Aktiv="xx"  # momentan aktive Pumpenschaltung
GPIO.setmode(GPIO.BCM) # We will be using the BCM GPIO numbering
GPIO_CONTROL = 17 # Select a control GPIO
GPIO.setup(GPIO_CONTROL, GPIO.OUT) # Set CONTROL to OUTPUT mode


#degree_sign = u'\xb0' # degree sign
devices = DS18B20()
count = devices.device_count()
names = devices.device_names()


Klartext='P-kalt ','Warmwasser ','P-heiss ','Raumtemp ' # Bezeichnung der Tempsensoren
Zeile=['aa','bb','cc']
n=[1,2,3,4]  # neue Werte für csv File
a=[1,2,3,4] # letzte ins csv File geschriebenen Werte
Restzeit=21
Endzeit=22


def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(17, GPIO.OUT)


def getTemperature():
    temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
    return temp

def rest():
    global Endzeit, Restzeit, Pumpe_Status , Zeile, Klartext
    global n,a
    
    Restzeit=math.trunc(Endzeit-time.time())  #chm '%6.2f' %  Kommastellen abschneiden, Zeitformat
    if Restzeit<0:
        Restzeit=0

    if Restzeit==0:
        GPIO.output(GPIO_CONTROL, GPIO.HIGH) #Pumpe deaktivieren
    
    strom=[1,2,3]
    z=0
    GAIN=1
    while z<=2:
        strom[z] = adc.read_adc(0, gain=GAIN) # Read the ADC channel 0 value
        z=z+1
    #print(strom)
    grenze=50 # Grenzwert bei dem die Pumpe EIN ist
    if max(strom)-min(strom)>grenze:
        Pumpe_Status='EIN'
    else:
        Pumpe_Status='AUS'
#    print ("n vorher",n)
 #   print ("a vorher",a)

    n[0]=str(round(devices.tempC(1),1))
    n[1]=str(round(devices.tempC(2),1))
    n[2]=str(round(devices.tempC(0),1))
    n[3]=str(round(devices.tempC(3),1))
    n[0]=str(time.time())
    print(n)
    print(a)
    n[0]=str(time.time())
    print(n)
    print(a)


    Zeile[0]=Klartext[1] + n[0]+'°C'
    Zeile[1]=Klartext[2] + n[1]+'°C --- '+Klartext[0] + n[2]+'°C'
    Zeile[2]=Klartext[3] + n[3]+'°C'


  #  print("n nachher",n)
   # print("a nachher",a)
    
    if a==n:
        print("gleich")
    else:
        print("unterschied")
        a=n
    print("----")

    file = open('FWM_Test.csv', 'a')   # chm ein File pro Tag
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([datetime.date.today(),datetime.datetime.now().strftime("%H:%M:%S"),
        round(devices.tempC(0),1),round(devices.tempC(1),1)])

    file.close()   # chm immer sofort wieder schließen

    threading.Timer(10, rest).start()



class MyServer(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        html = '''
           <html>
            <head>
                <title>Warmwasser</title>
                <meta http-equiv="refresh" content="3">
                <meta charset="UTF-8">
            </head>
           <body 
            style="width:960px; margin: 20px auto;font-size:200%">
           <h1>Warmwassersteuerung</h1>
           
           <form action="/" method="POST">
               Dauer :
               <input type="submit" name="submit" value="10min_EIN" style="padding:20px;margin=20px;font-size:160%">
               <input type="submit" name="submit" value="30min_EIN" style="padding:20px;font-size:160%">
               <input type="submit" name="submit" value="AUS" style="padding:20px;font-size:160%">
           </form>
           <p><br/>Restzeit: {}min {}s <br/><br/>Aktives Programm: {} <br/><br/>Pumpe: {}<br/><br/></p>
           <p>{}</p>
           <p>{}</p>
           <p>{}</p>
           </body>
           </html>
        '''
        #temp = getTemperature()
        self.do_HEAD()
        #self.wfile.write(html.format(temp[5:],Endzeit).encode("utf-8"))
        restminuten=math.trunc(Restzeit/60)
        restsekunden=Restzeit-60*restminuten
        self.wfile.write(html.format(restminuten,restsekunden,P_Aktiv,Pumpe_Status,
            Zeile[0],
            Zeile[1],
            Zeile[2]).encode("utf-8"))
        #print(tempSensorWert)


    def do_POST(self):
        global Endzeit, Restzeit, P_Aktiv
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]

        setupGPIO()

        if post_data == '10min_EIN':
            GPIO.output(17, GPIO.LOW) #Pumpe aktivieren
            startzeit = time.time()
            dauer=60*10
            Endzeit=startzeit + dauer
            Restzeit=dauer
            P_Aktiv="10-min"

        if post_data == '30min_EIN':
            GPIO.output(17, GPIO.LOW) #Pumpe aktivieren
            startzeit = time.time()
            dauer=60*30
            Endzeit=startzeit + dauer
            Restzeit=dauer
            P_Aktiv="30-min"    

        if post_data == 'AUS':
            Endzeit=time.time() #Restzeit auf 0 setzen
            Restzeit=0
            GPIO.output(GPIO_CONTROL, GPIO.HIGH) #Pumpe deaktivieren
            P_Aktiv="AUS"
        #print("LED is {}".format(post_data))
        self._redirect('/')  # Redirect back to the root url


def main():
    print("Hauptprogramm")
    rest()


# # # # # Main # # # # #

if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)
    #print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        main()
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
        GPIO.cleanup()
