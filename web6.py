#!/usr/bin/env python3
# coding=utf-8
# padding eingebaut
# kompletter Umbau

import RPi.GPIO as GPIO
import os, time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading


host_name = '192.168.178.40'  # IP Address of Raspberry Pi
host_port = 8000

GPIO.setmode(GPIO.BCM) # We will be using the BCM GPIO numbering
GPIO_CONTROL = 17 # Select a control GPIO
GPIO.setup(GPIO_CONTROL, GPIO.OUT)  # Set CONTROL to OUTPUT mode

Endzeit=0
Restzeit=0


"""
def rest():
    global Endzeit, Restzeit 
    #print('Some magic')
    Restzeit=Endzeit-time.time()
    print (Restzeit)
    if Restzeit<0:
        GPIO.output(17, GPIO.HIGH) #Pumpe deaktivieren
    threading.Timer(10, rest).start()
"""    

def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(17, GPIO.OUT)


def getTemperature():
    temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
    return temp


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
        #global Restzeit
        html = '''
           <html>
            <head>
                <title>Warmwasser</title>
                <meta http-equiv="refresh" content="3">  
            </head>
           <body 
            style="width:960px; margin: 20px auto;font-size:160%">
           <h1>Warmwassersteuerung</h1>
           <p>Current GPU temperature is {} Restzeit:{} </p>
           <form action="/" method="POST">
               Dauer: 
               <input type="submit" name="submit" value="1min_EIN" style="padding:20px">
               <input type="submit" name="submit" value="30min_EIN" style="padding:20px">
               <input type="submit" name="submit" value="AUS" style="padding:20px">
           </form>
           </body>
           </html>
        '''
        temp = getTemperature()
        self.do_HEAD()
        self.wfile.write(html.format(temp[5:],Restzeit).encode("utf-8"))

    def do_POST(self):
        global Endzeit
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]

        setupGPIO()

        if post_data == '1min_EIN':
            GPIO.output(17, GPIO.LOW) #Pumpe aktivieren
            startzeit = time.time()
            dauer=60
            Endzeit=startzeit + dauer
        if post_data == 'AUS':
            GPIO.output(17, GPIO.HIGH) #Pumpe deaktivieren

        print("LED is {}".format(post_data))
        self._redirect('/')  # Redirect back to the root url


def main():
   # global dauer
   # dauer=0
   # rest()
    print("Hauptprogramm")
    """
    dauer=20 #Dauer der Warmwasserbereitstellung
    spanne=5 #alle x s wird eine Meldung über verbleibende Zeit
    print('Ist EIN -',time.asctime())    
    GPIO.output(GPIO_CONTROL, False)
    while dauer>0:
        # das soll aufs Handy geschrieben werden
        print('noch',dauer,'s.')
        time.sleep(spanne)
        dauer=dauer-spanne
    GPIO.output(GPIO_CONTROL, True)
    print('Ist AUS -',time.asctime())      
    GPIO.cleanup()
    dauer=17
    """

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
