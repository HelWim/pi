#!/usr/bin/python3
# coding=utf-8

import time

n=[1,2,3,4]  # neue Werte für csv File
a=[1,2,3,4] # letzte ins csv File geschriebenen Werte


print('[press ctrl+c to end the script]') 
try: # Main program loop
    while True:
        print(n)
        print(a)
        n[0]=str(time.time())
        print(n)
        print(a)

        if a==n:
            print("gleich")
        else:
            print("unterschied")
            a=list(n)
        #time.sleep(5)
        Eingabe=input("Press Enter")
        print("----")
      





# Scavenging work after the end of the program
except KeyboardInterrupt:
    print('Script end!')
  
