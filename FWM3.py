#!/usr/bin/env python3
# coding=utf-8
# Umstellen auf AZ-delviery Temperaturauslesen
# 3 Diagramme
# neue Steckerplatine für Temperatursensoren
# 16.10.21 Pfad ergänzt
'''
sudo nano /etc/rc.local


sudo dtoverlay w1-gpio gpiopin=4 pullup=0
sudo dtoverlay w1-gpio gpiopin=17 pullup=0
sudo dtoverlay w1-gpio gpiopin=27 pullup=0
ls -l /sys/bus/w1/devices/

nohup python3 FWM3.py &
'''

import RPi.GPIO as GPIO
import os, time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time, datetime
import Adafruit_ADS1x15
import math
from DS18B20classFile import DS18B20
import csv, statistics


adc = Adafruit_ADS1x15.ADS1115() # Create an ADS1115 ADC (16-bit) instance

host_name = '192.168.178.40'  # IP Address of Raspberry Pi
host_port = 8000

Pumpe_Status="AUS"
P_Aktiv="xx"  # momentan aktive Pumpenschaltung

# Ansteuerung Relais
GPIO.setmode(GPIO.BCM) # We will be using the BCM GPIO numbering
GPIO.setwarnings(False) # wieso? kommt vom Ultraschallsensor
GPIO_CONTROL = 5 # Select a control GPIO, 21.3.21 vorher 17
GPIO.setup(GPIO_CONTROL, GPIO.OUT) # Set CONTROL to OUTPUT mode

TRIG = 23  # BCM 4 funktioniert nicht gut, da er von der One-wire Schnittstelle auch benutzt werden kann
ECHO = 24
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, False)

# für Level Zysterne
L1_werte=[]  #laufende Messungen
L1_60_werte=[] # Messungen der letzen 10min, rollierend
L1_alt=0
L1=0
distance1=0


#degree_sign = u'\xb0' # degree sign
devices = DS18B20()
count = devices.device_count()
names = devices.device_names()


Klartext='P-kalt ','Warmwasser ','P-heiss ','T Raum ' # Bezeichnung der Tempsensoren
Zeile=['aa','bb','cc','dd']
Restzeit=21
Endzeit=22
Alarmtext="ok" #wenn Flow switch hängt
Delay_endzeit=0
t_ww_dn=0 #Devicenummer vom Warmwasser-Temperatursensor
t_ph_dn=0 #Devicenummer vom Puffer-heiss-Temperatursensor
t_pk_dn=0 #Devicenummer vom Puffer-kalt-Temperatursensor
t_raum_dn=0 #Devicenummer vom Raumtemp-Temperatursensor
t_p1_dn=0 #Devicenummer vom Puffertemperatursensor erster von unten
t_p2_dn=0 #Devicenummer vom Puffertemperatursensor zweiter von unten
t_p3_dn=0 #Devicenummer vom Puffertemperatursensor dritter von unten
t_p4_dn=0 #Devicenummer vom Puffertemperatursensor vierter von unten
i_pt=0 # Anch wievielen Lesezyklen die Puffertemperaturen am Handytrend angezeigt werden

t_p1=20 # Puffertemperatur erste von unten
t_p2=20 # Puffertemperatur zweite von unten
t_p3=20 # Puffertemperatur dritte von unten
t_p4=20 # Puffertemperatur vierte von unten

F_Name="x"
Pfad="/home/pi/"
a=[1,2,3,4,5,6,7]  # alte Werte für csv File
X_werte=[] # X-Achse 1. Diagramm
Y1_werte=[]
Y2_werte=[]
Y3_werte=[]
Y4_werte=[]
Y5_werte=[]
XA_werte=[] # X-Achse 2. Diagramm
YA1_werte=[] 
YA2_werte=[] 
YA3_werte=[] 
YA4_werte=[] 
XB_werte=[] # X-Achse 3. Diagramm
YB1_werte=[] 
YB2_werte=[] 
YB3_werte=[] 
YB4_werte=[] 


P_Endzeit=22 # Endzeit für Druckdiagramm
Puffer_Endzeit=22 # Endzeit für Auslesen der Puffertemperaturen

rf=6 #refresh Zeit html

def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(GPIO_CONTROL, GPIO.OUT)


def getTemperature():  #CPU Temperatur
    temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
    return temp

def rest():
    global Endzeit, Restzeit, Pumpe_Status , Zeile, Klartext, Alarmtext
    global file, Delay_endzeit
    global X_werte, Y1_werte, Y2_werte, a  #Hier fehlt Y3:werte und es geht trotzdem
    global XA_werte, YA1_werte,YA2_werte,YA3_werte,YA4_werte
    global XB_werte, YB1_werte,YB2_werte,YB3_werte,YB4_werte
    global Pfad, F_Name, writer, P_Endzeit, Puffer_Endzeit
    global t_p1,t_p2,t_p3,t_p4, i_pt
    global L1

    threading.Timer(20, rest).start() # damit es auch bei einem I/O Fehler weiter geht
    # nach 20s wird dieses Unterprogamm wieder aufgerufen
    
    # Ausschalten der Pumpe wenn Zeit abgelaufen ist
    Restzeit=math.trunc(Endzeit-time.time())  #chm '%6.2f' %  Kommastellen abschneiden, Zeitformat
    if Restzeit<0:
        Restzeit=0
    if Restzeit==0:
        GPIO.output(GPIO_CONTROL, GPIO.HIGH) #Pumpe deaktivieren
    
    #Stromsensor um festzustellen ob Pumpe läuft
    strom=[1,2,3]
    z=0
    GAIN=1
    while z<=2:
        strom[z] = adc.read_adc(0, gain=GAIN) # Read the ADC channel 0 value
        z=z+1
    grenze=50 # Grenzwert des Rauschens bei dem die Pumpe EIN ist
    if max(strom)-min(strom)>grenze:
        Pumpe_Status='EIN'
        ps=30  # damit er im Temperaturdiagramm gut sichtbar ist
    else:
        Pumpe_Status='AUS'
        ps=0

    #Drucksensor Heizung
    values=[1,2]
    z=0
    while z<=1:
        values[z] = adc.read_adc(1, gain=GAIN) # Read the ADC channel 1 value
        z=z+1
        mittel=sum(values)/len(values)
        druck=(mittel-3936)/(24834-3936)*4 #alt:26608
        time.sleep(1)

    #Drucksensor Wasserwerk
    druck_ww=(adc.read_adc(2, gain=GAIN)-3936)/(24834-3936)*4 #alt:26608
    druck_ww=round(druck_ww,2)  

    # hier Level Zysterne abrufen
    ultra1()
    #print (L1)

    n=[1,2,3,4,5,6,7,8,9,10,11,12]  # neue Werte für csv File
    #a=[1,2,3,4,5]  # alte Werte für csv File
    t_ww=round(devices.tempC(t_ww_dn),1)  #Warmwasser
    t_ph=round(devices.tempC(t_ph_dn),1)  #P-heiss
    t_pk=round(devices.tempC(t_pk_dn),1)  #P-kalt
    t_raum=round(devices.tempC(t_raum_dn),1)  #Raumtemperatur
    p=round(druck,2) # Druck Heizung

    #P-Kalt > Warmwasser, nur das erste Event speichern  chm Unterschied ' und ""
    delay=120 # Anzugsverzögerung des Alarms in Sekunden
    if Pumpe_Status=='EIN' and t_pk > t_ww and Alarmtext=="ok":
        if Delay_endzeit==0:
            Delay_endzeit=time.time()+delay
            #print('los',datetime.datetime.now())
        if time.time()>Delay_endzeit:      
            Alarmtext="ALARM: "+ datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
            #print('delay',datetime.datetime.now())
            Delay_endzeit=0
    astatus=0 if Alarmtext == "ok" else 1  #Alarmstatus

    spanne_puffer=120 # in welchen Zeitabständen die Puffertemperaturen gelesen werden, in Sekunden
    if time.time()>Puffer_Endzeit:
        Puffer_Endzeit=time.time() + spanne_puffer # neue Endzeit  
        t_p1=round(devices.tempC(t_p1_dn),1) # Puffertemperatur erste von unten
        t_p2=round(devices.tempC(t_p2_dn),1) # Puffertemperatur zweite von unten
        t_p3=round(devices.tempC(t_p3_dn),1) # Puffertemperatur dritte von unten
        t_p4=round(devices.tempC(t_p4_dn),1) # Puffertemperatur vierte von unten

        #Speichern der Werte für den Trend
        #Bei jedem Durchlauf - noch zu ändern
        i_pt=i_pt+1
        if i_pt == 10: # jeden 10. Zyklus wird ein Punkt am Handydiagramm gesetzt
            i_pt=0
            XB_werte.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            YB1_werte.append(t_p1)
            YB2_werte.append(t_p2)
            YB3_werte.append(t_p3)
            YB4_werte.append(t_p4)

    # in dieser Reihenfolge werden die Daten ins csv File geschrieben
    n[0]=t_ww
    n[1]=t_ph
    n[2]=t_pk
    n[3]=t_raum
    n[4]=p #Druck in Heizung
    n[5]=ps  # Pumpenstatus
    n[6]=astatus #Alarmstatus
    n[7]=t_p1 #Puffertemperatur erster von unten
    n[8]=t_p2 #Puffertemperatur zweite von unten
    n[9]=t_p3 #Puffertemperatur dritte von unten
    n[10]=t_p4 #Puffertemperatur dritte von unten
    n[11]=L1 #Puffertemperatur dritte von unten
        
    Zeile[0]=Klartext[1] + str(n[0])+'°C'
    Zeile[1]=Klartext[2] + str(n[1])+'°C --- '+Klartext[0] + str(n[2])+'°C'
    Zeile[2]=Klartext[3] + str(n[3])+'°C --- Zysterne ' + str(n[11]) +'m'  #Raumtemp, Zysterne
    Zeile[3]='Druck: '+ str(n[4]) + 'barg'

    if F_Name != Pfad+str(datetime.date.today())+".csv": #neuer Tag
        file.close()
        F_Name = Pfad+str(datetime.date.today())+".csv"
        file = open(F_Name, 'a') 
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #print(n)
    #print(a)
    gleich=1

    if abs(n[0]-a[0])>0.2 :
        gleich=0
    if abs(n[1]-a[1])>0.2 :
        gleich=0
    if abs(n[2]-a[2])>0.2 :
        gleich=0
    if abs(n[3]-a[3])>0.2 :
        gleich=0
    if abs(n[4]-a[4])>0.05 :
        gleich=0
    if n[5] != a[5] :
        gleich=0
    if n[6] != a[6] :
        gleich=0
    # die anderen Werte werden mitgeschrieben

    #print (gleich)

    if gleich==0: #File schreiben wenn die Daten sich geändert haben
        writer.writerow([datetime.date.today(),datetime.datetime.now().strftime("%H:%M:%S"),   
            n[0],n[1],n[2],n[3],n[4],n[5],n[6],n[7],n[8],n[9],n[10],n[11]])
        #print(datetime.date.today(),datetime.datetime.now().strftime("%H:%M:%S"),
            #   n[0],n[1],n[2],n[3],n[4])
        a=list(n)

    #die letzten Werte für Handy-Trend 1 speichern, bei jedem Durchlauf
    X_werte.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    Y1_werte.append(t_ww)
    Y2_werte.append(t_pk)
    Y3_werte.append(t_ph)
    Y4_werte.append(ps)
    Y5_werte.append(druck_ww*10) #zehfacher Wert damit Skala passt

    if len(X_werte)>50:
        x=X_werte.pop(0)
        x=Y1_werte.pop(0)
        x=Y2_werte.pop(0)
        x=Y3_werte.pop(0)
        x=Y4_werte.pop(0)
        x=Y5_werte.pop(0)
    #print(X_werte,Y1_werte)

    spanne=1200 # Anstand für die Diagrammpunkte für Handy-Diagramm 2 in Sekunden
    if time.time()>P_Endzeit:
        P_Endzeit=time.time() + spanne # neue Endzeit
        XA_werte.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        YA1_werte.append(p)   #Druck
        YA2_werte.append(ps)   #Pumpenstatus, momentan nicht verwendet
        YA3_werte.append(druck_ww*0.5) # die Hälfte wegen Skala
        YA4_werte.append(L1) # Ultra Zysterne

    if len(XA_werte)>100:
        x=XA_werte.pop(0)
        x=YA1_werte.pop(0)
        x=YA2_werte.pop(0)  #Pumpenstatus, momentan nicht verwendet
        x=YA3_werte.pop(0) # Druck Wasserwerk
        x=YA4_werte.pop(0) # Ultra Zysterne

    if len(XB_werte)>50:
        x=XB_werte.pop(0)
        x=YB1_werte.pop(0)
        x=YB2_werte.pop(0)
        x=YB3_werte.pop(0)
        x=YB4_werte.pop(0)

    #print(XA_werte,YA1_werte,YA2_werte)



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
        global rf
        print ("do get start")
        html = '''
           <html>
            <head>
                <title>Warmwasser</title>
                <meta http-equiv="refresh" content={}>
                <meta charset="UTF-8">
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
           <body 
            style="width:960px; margin: 20px auto;font-size:200%">
           <h1>Warmwassersteuerung</h1>
           
           <form action="/" method="POST">
               <input type="submit" name="submit" value="10min_EIN" style="padding:20px;margin=20px;font-size:160%">
               <input type="submit" name="submit" value="30min_EIN" style="padding:20px;font-size:160%">
               <input type="submit" name="submit" value="AUS" style="padding:20px;font-size:160%">
           </form>
           <p><br/>Restzeit: {}min {}s <br/><br/>Aktives Programm: {} <br/>Pumpe: {}<br/><br/></p>
           <p>{}</p>
           <p>{}</p>
           <p>{}</p>
           <p>{}</p>
           <p><br/>Flow Switch: {}</p>
           <form action="/" method="POST">
               <input type="submit" name="submit" value="Quitieren" style="padding:20px;font-size:160%">
               <input type="submit" name="submit" value="Refresh" style="padding:20px;font-size:160%">
           </form>
           <p>Refresh: {}s</p>

           <div id="diagramm"></div>
           <script> 
            var trace1 = {{
                type: "scatter",
                mode: "lines",
                name: 't_WW',
                x:{},
                y:{},
                line: {{color: '#ffa500'}}
            }}

            var trace2 = {{
                type: "scatter",
                mode: "lines",
                name: 't_pk',
                x:{},
                y:{},
                line: {{color: '#0000ff'}}
            }}

            var trace3 = {{
                type: "scatter",
                mode: "lines",
                name: 't_ph',
                x:{},
                y:{},
                line: {{color: '#ff0000'}}
            }}

            var trace4 = {{
                type: "scatter",
                mode: "lines",
                name: 'Pumpe',
                x:{},
                y:{},
                line: {{color: '#808080'}}
            }}
            var trace5 = {{
                type: "scatter",
                mode: "lines",
                name: 'Druck_WW',
                x:{},
                y:{},
                line: {{color: '#808080'}}
            }}

            var data = [trace3,trace1,trace2,trace4,trace5];

            var layout = {{
                title: 'Warmwasser',
                yaxis: {{
                    autorange: false,
                    range: [10, 60],
                    type: 'linear'
                }}
            }};
            Plotly.newPlot('diagramm', data, layout);
           </script>

           <div id="diagramm2"></div>
           <script> 
            var trace1 = {{
                type: "scatter",
                mode: "lines",
                name: 'Druck Heizung',
                x:{},
                y:{},
                line: {{color: '#17BECF'}}
            }}

            var trace2 = {{
                type: "scatter",
                mode: "lines",
                name: 'Druck WW',
                x:{},
                y:{},
                line: {{color: '#808080'}}
            }}
            var trace3 = {{
                type: "scatter",
                mode: "lines",
                name: 'Zysterne',
                x:{},
                y:{},
                line: {{color: '#ffa500'}}
            }}            
            var data = [trace1,trace2,trace3];

            var layout = {{
                title: 'Druck, Level',
                yaxis: {{
                    autorange: false,
                    range: [0.5, 2.5],
                    type: 'linear'
                }}
            }};
            Plotly.newPlot('diagramm2', data, layout);
           </script>

           <div id="diagramm3"></div>
           <script> 
            var trace1 = {{
                type: "scatter",
                mode: "lines",
                name: 't_p1',
                x:{},
                y:{},
                line: {{color: '#0000ff'}}
            }}

            var trace2 = {{
                type: "scatter",
                mode: "lines",
                name: 't_p2',
                x:{},
                y:{},
                line: {{color: '#1e90ff'}}
            }}

            var trace3 = {{
                type: "scatter",
                mode: "lines",
                name: 't_p3',
                x:{},
                y:{},
                line: {{color: '#ffa500'}}
            }}

            var trace4 = {{
                type: "scatter",
                mode: "lines",
                name: 't_p4',
                x:{},
                y:{},
                line: {{color: '#ff0000'}}
            }}


            var data = [trace4,trace3,trace2,trace1];

            var layout = {{
                title: 'Puffer',
                yaxis: {{
                    autorange: false,
                    range: [10, 60],
                    type: 'linear'
                }}
            }};
            Plotly.newPlot('diagramm3', data, layout);
           </script>

           </body>
           </html>
        '''

        #temp = getTemperature()
        self.do_HEAD()
        #self.wfile.write(html.format(temp[5:],Endzeit).encode("utf-8"))
        restminuten=math.trunc(Restzeit/60)
        restsekunden=Restzeit-60*restminuten
        self.wfile.write(html.format(rf,restminuten,restsekunden,P_Aktiv,Pumpe_Status,
            Zeile[0],
            Zeile[1],
            Zeile[2],Zeile[3],
            Alarmtext,
            rf,
            X_werte,Y1_werte,X_werte,Y2_werte,X_werte,Y3_werte,X_werte,Y4_werte,X_werte,Y5_werte,
            XA_werte,YA1_werte,XA_werte,YA3_werte,XA_werte,YA4_werte,
            XB_werte,YB1_werte,XB_werte,YB2_werte,XB_werte,YB3_werte,XB_werte,YB4_werte
            ).encode("utf-8"))
        #print(tempSensorWert)
        #print(XA_werte,YA1_werte,XA_werte,YA2_werte)
        print("Do Get end")


    def do_POST(self):
        global Endzeit, Restzeit, P_Aktiv, Alarmtext, rf
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]

        setupGPIO()

        if post_data == '10min_EIN':
            GPIO.output(GPIO_CONTROL, GPIO.LOW) #Pumpe aktivieren
            startzeit = time.time()
            dauer=60*10
            Endzeit=startzeit + dauer
            Restzeit=dauer
            P_Aktiv="10-min"

        if post_data == '30min_EIN':
            GPIO.output(GPIO_CONTROL, GPIO.LOW) #Pumpe aktivieren
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

        if post_data == 'Refresh':
            if rf==6:
                rf=2000
            else:
                rf=6


        #print("LED is {}".format(post_data))
        self._redirect('/')  # Redirect back to the root url

def serverR():
    #Schließt und öffnet den Server regelmäßig
    # das funktioniert so nicht
    threading.Timer(90, serverR).start()
    http_server.server_close()
    http_server = HTTPServer((host_name, host_port), MyServer)
    http_server.serve_forever()

def ultra1():
    global L1_werte, L1_alt, L1, L1_60_werte, distance1
    # grosser Ultraschallsensor
    #print("ultra1")
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
    while GPIO.input(ECHO) == 1 and time.time()<mt:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150 /100 # auf m umrechnen
    distance = round(distance, 2)
    #print("distance",distance)
    
    if distance>300:
        distance=300
    distance1=("%.2f") % distance  # was soll hier disance1?
    L1_werte.append(distance)
    #L1=round(sum(L1_werte)/len(L1_werte),1)  
    L1=round(statistics.median(L1_werte),2)  
    #print("L1 median",L1_werte,statistics.median(L1_werte))

    if len(L1_werte)>14:  # bei 2s Pause sind da 1/2h min Rolling average
        x=L1_werte.pop(0)
    L1_60_werte.append(L1)
    if len(L1_60_werte)>1800:  # auf 1h begrenzen
        x=L1_60_werte.pop(0)    

    #print(L1_werte)
    #print (L1)
    #print(datetime.datetime.now().strftime("%H:%M:%S"),"Ultra1: Distance is {} cm".format(L1), "aktuell=",distance1)

def main():
    global file, writer, F_Name, Pfad
    global t_ww_dn, t_ph_dn, t_pk_dn, t_raum_dn
    global t_p1_dn, t_p2_dn, t_p3_dn, t_p4_dn
    print("Hauptprogramm")
    F_Name=Pfad+str(datetime.date.today())+".csv"
    print(F_Name)
    #file = open('FWM_Test.csv', 'a')  
    file = open(F_Name, 'a') 
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    #Feststellen welche Devicenummer ein Temperatursensir hat
    print('\nReading temperature, number of sensors: {}'
			.format(count))
    i = 0   
    while i < count:
        if names[i]=='28-3c01d075619c':
            t_ww_dn=i
        if names[i]=='28-3c01d075af0e':
            t_pk_dn=i
        if names[i]=='28-3c01d075bdf3':
            t_ph_dn=i
        if names[i]=='28-012033389e18':
            t_raum_dn=i
        if names[i]=='28-01203395e5cc':
            t_p4_dn=i #Devicenummer vom Puffertemperatursensor vierter von unten
        if names[i]=='28-0120333abd5d':
            t_p3_dn=i #Devicenummer vom Puffertemperatursensor dritter von unten            
        if names[i]=='28-0120333dff2b':
            t_p2_dn=i #Devicenummer vom Puffertemperatursensor zweiter von unten 
        if names[i]=='28-0120333b1a7b':
            t_p1_dn=i #Devicenummer vom Puffertemperatursensor erster von unten 
        
        i=i+1
    
    print(t_ww_dn, t_ph_dn, t_pk_dn,t_raum_dn)


    rest()
    #serverR()  # funktioniert so leider nicht


# # # # # Main # # # # #

if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)

    try:
        main()
        http_server.serve_forever()
        print("try nochmal")
        http_server.serve_forever()

    except KeyboardInterrupt:
        http_server.server_close()
        GPIO.cleanup()
        file.close()


    '''
    except err:
        print(err, datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S"))
        #http_server.server_close()
        #http_server.serve_forever()
    '''

    '''
    except OSError:
        print("OS Error", datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S"))
    else:
        print("Allgemeiner Fehler", datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S"))
    '''
    
    '''
    nohup python3 FWM3.py &
    sudo dtoverlay w1-gpio gpiopin=4 pullup=0
    sudo dtoverlay w1-gpio gpiopin=17 pullup=0
    sudo dtoverlay w1-gpio gpiopin=27 pullup=0
    '''

