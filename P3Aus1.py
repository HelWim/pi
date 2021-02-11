#!/usr/bin/python
# coding=utf-8
# messprogramm.py
#------------------------------------------------------------

import os, sys, time

# Das war eine Python2 Datei
# Nur beim Print-Befehl Klammern eingebaut und es geht auf Python3
# 6.1.21 hinzufügen von Klartext
# 16.1.21 hinzufügen der Prozessortemperatur

# Global für vorhandene Temperatursensoren
tempSensorBezeichnung = [] #Liste mit den einzelnen Sensoren-Kennungen
tempSensorAnzahl = 0 #INT für die Anzahl der gelesenen Sensoren
tempSensorWert = [] #Liste mit den einzelnen Sensor-Werten

# Global für Programmstatus / 
programmStatus = 1 

def get_cpu_temp():
    """
    Obtains the current value of the CPU temperature.
    :returns: Current value of the CPU temperature if successful, zero value otherwise.
    :rtype: float
    """
    # Initialize the result.
    result = 0.0
    # The first line in this file holds the CPU temperature as an integer times 1000.
    # Read the first line and remove the newline character at the end of the string.
    if os.path.isfile('/sys/class/thermal/thermal_zone0/temp'):
        with open('/sys/class/thermal/thermal_zone0/temp') as f:
            line = f.readline().strip()
        # Test if the string is an integer as expected.
        if line.isdigit():
            # Convert the string with the CPU temperature to a float in degrees Celsius.
            result = float(line) / 1000
    # Give the result back to the caller.
    return result

def ds1820einlesen():
    global tempSensorBezeichnung, tempSensorAnzahl, programmStatus
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
    global tempSensorBezeichnung, tempSensorAnzahl, tempSensorWert, programmStatus
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
        programmStatus = 0
    #print (tempSensorWert)
#Programminitialisierung
ds1820einlesen() #Anzahl und Bezeichnungen der vorhandenen Temperatursensoren einlesen

# Temperaturausgabe in Schleife
while programmStatus == 1:
    x = 0
    ds1820auslesen()
    Klartext='Puffer-kalt ','Warmwasser  ','Puffer heiss','Raumtemp    '
#    print "Sensorbezeichnung und Temperaturwert:"
    print(time.asctime())
    while x < tempSensorAnzahl:
#        print (tempSensorBezeichnung[x] , Klartext[x]," " , tempSensorWert[x] , " °C")
        print (Klartext[x]," " , tempSensorWert[x] , " °C")
        x = x + 1
    #print (tempSensorWert)
#    time.sleep(2)
#    pt=sys/class/thermal/thermal_zone0/temp
    print('CPUtemp         {:.2f} °C'.format(get_cpu_temp()))
    print ("\n")
    time.sleep(3)
   
# Programmende durch Veränderung des programmStatus
print ("Programm wurde beendet.")
