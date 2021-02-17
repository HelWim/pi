#!/usr/bin/env python3
# coding=utf-8
# Umstellen auf AZ-delviery Temperaturauslesen

import RPi.GPIO as GPIO
import os, time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time, datetime
import Adafruit_ADS1x15
import math
from DS18B20classFile import DS18B20
import csv

import plotly.graph_objects as go


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
Zeile=['aa','bb','cc','dd']
Restzeit=21
Endzeit=22
Alarmtext="ok" #wenn Flow switch hängt
Delay_endzeit=0

def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(17, GPIO.OUT)


def getTemperature():
    temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
    return temp

def rest():
    global Endzeit, Restzeit, Pumpe_Status , Zeile, Klartext, Alarmtext
    global file, Delay_endzeit
    threading.Timer(15, rest).start() # damit es auch bei einem I/O Fehler weiter geht
    
    Restzeit=math.trunc(Endzeit-time.time())  #chm '%6.2f' %  Kommastellen abschneiden, Zeitformat
    if Restzeit<0:
        Restzeit=0
    if Restzeit==0:
        GPIO.output(GPIO_CONTROL, GPIO.HIGH) #Pumpe deaktivieren
    
    #Stromsensor
    strom=[1,2,3]
    z=0
    GAIN=1
    while z<=2:
        strom[z] = adc.read_adc(0, gain=GAIN) # Read the ADC channel 0 value
        z=z+1
    grenze=50 # Grenzwert des Rauschens bei dem die Pumpe EIN ist
    if max(strom)-min(strom)>grenze:
        Pumpe_Status='EIN'
    else:
        Pumpe_Status='AUS'

    #Drucksensor
    values=[1,2]
    z=0
    while z<=1:
        values[z] = adc.read_adc(1, gain=GAIN) # Read the ADC channel 1 value
        z=z+1
        mittel=sum(values)/len(values)
        druck=(mittel-3936)/(26608-3936)*4


    n=[1,2,3,4,5]  # neue Werte für csv File
    t_ww=round(devices.tempC(1),1)  #Warmwasser
    t_ph=round(devices.tempC(2),1)  #P-heiss
    t_pk=round(devices.tempC(0),1)  #P-kalt
    t_raum=round(devices.tempC(3),1)  #Raumtemperatur
    p=round(druck,2) # Druck Heizung
    n[0]=t_ww
    n[1]=t_ph
    n[2]=t_pk
    n[3]=t_raum
    n[4]=p

    #P-Kalt > Warmwasser, nur das erste Event speichern  chm Unterschied ' und ""

    delay=5 # Anzugsverzögerung des Alarms
    if Pumpe_Status=='EIN' and t_pk > t_ww and Alarmtext=="ok":
        if Delay_endzeit==0:
            Delay_endzeit=time.time()+delay
            print('los',datetime.datetime.now())
        if time.time()>Delay_endzeit:      
            Alarmtext="ALARM: "+ datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
            print('delay',datetime.datetime.now())
            Delay_endzeit=0



    Zeile[0]=Klartext[1] + str(n[0])+'°C'
    Zeile[1]=Klartext[2] + str(n[1])+'°C --- '+Klartext[0] + str(n[2])+'°C'
    Zeile[2]=Klartext[3] + str(n[3])+'°C'
    Zeile[3]='Druck: '+ str(n[4]) + 'barg'

    #file = open('FWM_Test.csv', 'a')  
    #writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([datetime.date.today(),datetime.datetime.now().strftime("%H:%M:%S"),
        n[0],n[1],n[2],n[3],n[4]])
    print(datetime.date.today(),datetime.datetime.now().strftime("%H:%M:%S"),
        n[0],n[1],n[2],n[3],n[4])

    #file.close()   # chm immer sofort wieder schließen





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
                <meta http-equiv="refresh" content="5">
                <meta charset="UTF-8">
                <script src="first_figure.html"></script>
            </head>
           <body 
            style="width:960px; margin: 20px auto;font-size:200%">
           <h1>Warmwassersteuerung</h1>
           
           <form action="/" method="POST">
               <input type="submit" name="submit" value="10min_EIN" style="padding:20px;margin=20px;font-size:160%">
               <input type="submit" name="submit" value="30min_EIN" style="padding:20px;font-size:160%">
               <input type="submit" name="submit" value="AUS" style="padding:20px;font-size:160%">
           </form>
           <p><br/>Restzeit: {}min {}s <br/><br/>Aktives Programm: {} <br/><br/>Pumpe: {}<br/><br/></p>
           <p>{}</p>
           <p>{}</p>
           <p>{}</p>
           <p>{}</p>
           <p><br/>Flow Switch: {}</p>
           <form action="/" method="POST">
               <input type="submit" name="submit" value="Quitieren" style="padding:20px;font-size:160%">
           </form>

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
            Zeile[2],Zeile[3],
            Alarmtext).encode("utf-8"))
        #print(tempSensorWert)
        fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
        fig.write_html('first_figure.html', auto_open=True)


    def do_POST(self):
        global Endzeit, Restzeit, P_Aktiv, Alarmtext
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

        if post_data == 'Quitieren':
            Alarmtext="ok"


        #print("LED is {}".format(post_data))
        self._redirect('/')  # Redirect back to the root url


def main():
    global file, writer
    print("Hauptprogramm")
    file = open('FWM_Test.csv', 'a')  
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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
        file.close()

