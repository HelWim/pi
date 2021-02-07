#!/usr/bin/env python3
# coding=utf-8


#Ausgehend von web3 - ändern bis das Refreg nicht mehr geht

import RPi.GPIO as GPIO
import os, time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time
import Adafruit_ADS1x15
import math

adc = Adafruit_ADS1x15.ADS1115() # Create an ADS1115 ADC (16-bit) instance

host_name = '192.168.178.40'  # IP Address of Raspberry Pi
host_port = 8000
Pumpe_Status="AUS"
P_Aktiv="xx"  # momentan aktive Pumpenschaltung
GPIO.setmode(GPIO.BCM) # We will be using the BCM GPIO numbering
GPIO_CONTROL = 17 # Select a control GPIO
GPIO.setup(GPIO_CONTROL, GPIO.OUT) # Set CONTROL to OUTPUT mode

# Global für vorhandene Temperatursensoren
tempSensorBezeichnung = [] #Liste mit den einzelnen Sensoren-Kennungen
tempSensorAnzahl = 0 #INT für die Anzahl der gelesenen Sensoren
tempSensorWert = [] #Liste mit den einzelnen Sensor-Werten
Klartext='P-kalt ','Warmwasser  ','P-heiss','Raumtemp    ' # Bezeichnung der Tempsensoren
Zeile=['aa','bb','cc']

Restzeit=21
Endzeit=22


def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(17, GPIO.OUT)

def ds1820einlesen():
    global tempSensorBezeichnung, tempSensorAnzahl
    #Verzeichnisinhalt auslesen mit allen vorhandenen Sensorbezeichnungen 28-xxxx
    try:
        for x in os.listdir("/sys/bus/w1/devices"):
            if (x.split("-")[0] == "28") or (x.split("-")[0] == "10"):
                tempSensorBezeichnung.append(x)
                tempSensorAnzahl = tempSensorAnzahl + 1
    except:
        # Auslesefehler
        print ("Der Verzeichnisinhalt konnte nicht ausgelesen werden.")
        programmStatus = 0

def ds1820auslesen():
    global tempSensorBezeichnung, tempSensorAnzahl, tempSensorWert
    x = 0
    try:
        # 1-wire Slave Dateien gem. der ermittelten Anzahl auslesen 
        while x < tempSensorAnzahl:
            dateiName = "/sys/bus/w1/devices/" + tempSensorBezeichnung[x] + "/w1_slave"
            file = open(dateiName)
            filecontent = file.read()
            file.close()
            # Temperaturwerte auslesen und konvertieren
            stringvalue = filecontent.split("\n")[1].split(" ")[9]
            sensorwert = float(stringvalue[2:]) / 1000
            temperatur = '%6.2f' % sensorwert #Sensor- bzw. Temperaturwert auf 2 Dezimalstellen formatiert
            tempSensorWert.insert(x,temperatur) #Wert in Liste aktualisieren
            x = x + 1
    except:
        # Fehler bei Auslesung der Sensoren
        print ("Die Auslesung der DS1820 Sensoren war nicht möglich.")
    """
    x = 0
    while x < tempSensorAnzahl:
        print (Klartext[x]," " , tempSensorWert[x] , " °C")
        x = x + 1
    #time.sleep(2)
    """

def getTemperature():
    temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
    return temp

def rest():
    global Endzeit, Restzeit, Pumpe_Status , Zeile, Klartext
    
    Restzeit=math.trunc(Endzeit-time.time())  #chm '%6.2f' %  Kommastellen abschneiden, Zeitformat
    if Restzeit<0:
        Restzeit=0
    #format = "%M:%S"  #chm
    #test=Restzeit(format)
    #print(test)
    #print (Restzeit)
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

    ds1820auslesen()
    Zeile[0]=Klartext[1] + tempSensorWert[1]+'°C'
    Zeile[1]=Klartext[2] + tempSensorWert[2]+'°C --- '+Klartext[0] + tempSensorWert[0]+'°C'
    Zeile[2]=Klartext[3] + tempSensorWert[3]+'°C'
    """
    x = 0
    while x < tempSensorAnzahl:
        print (Klartext[x]," " , tempSensorWert[x] , " °C")
        x = x + 1
    """

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
        #global tempSensorWert #nützt nichts
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
               <input type="submit" name="submit" value="1min_EIN" style="padding:20px;margin=20px;font-size:160%">
               <input type="submit" name="submit" value="30min_EIN" style="padding:20px;font-size:160%">
               <input type="submit" name="submit" value="AUS" style="padding:20px;font-size:160%">
           </form>
           <p><br/>Restzeit:{}min {}s <br/><br/>Aktives Programm: {} <br/><br/>Pumpe: {}<br/><br/></p>
           <p>{}</p>
           <p>{}</p>
           <p>{}</p>
           </body>
           </html>
        '''
        #temp = getTemperature()
        self.do_HEAD()
        #self.wfile.write(html.format(temp[5:],Endzeit).encode("utf-8"))
        #ds1820auslesen()  # dann geht gar nichts mehr
        restminuten=math.trunc(Restzeit/60)
        restsekunden=Restzeit-60*restminuten
        self.wfile.write(html.format(restminuten,restsekunden,P_Aktiv,Pumpe_Status,
            Zeile[0],
            Zeile[1],
            Zeile[2]).encode("utf-8"))
        #print(tempSensorWert)
        """
        print(Zeile[0])
        print(Zeile[1])
        print(Zeile[2])
        
        x = 0
        while x < tempSensorAnzahl:
            print (Klartext[x]," " , tempSensorWert[x] , " °C")
            x = x + 1
        time.sleep(2)
        """

    def do_POST(self):
        global Endzeit, Restzeit, P_Aktiv
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]

        setupGPIO()

        if post_data == '1min_EIN':
            GPIO.output(17, GPIO.LOW) #Pumpe aktivieren
            startzeit = time.time()
            dauer=60*1
            Endzeit=startzeit + dauer
            Restzeit=dauer
            P_Aktiv="1-min"

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
    ds1820einlesen() #Anzahl und Bezeichnungen der vorhandenen Temperatursensoren einlesen
    rest()


# # # # # Main # # # # #

if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        main()
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
        GPIO.cleanup()
