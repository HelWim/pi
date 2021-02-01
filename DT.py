#!/usr/bin/python3
# coding=utf-8
# Import required Python libraries
# Zum Ausprobieren von Zeitberechnungen
#from datetime import timedelta
import datetime, time

#print(time.asctime())
#print(datetime.timedelta(hours=10, minutes=16, seconds=32) - datetime.timedelta(hours=9))

# Store start time
start_time = time.time()

# Perform any action like print a string
#print("Printing this string takes ...")

# Store end time
end_time = time.time()


# Calculate the execution time and print the result
#print("%.10f seconds" % (end_time - start_time))
x=end_time - start_time
print("%.10f seconds" % x)
print(start_time)
print(x)
ziel_time=start_time + 10

while time.time() < ziel_time:
    print("jj")
    time.sleep(2)
print("fertig")
