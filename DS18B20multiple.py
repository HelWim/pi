import time
from DS18B20classFile import DS18B20

degree_sign = u'\xb0' # degree sign
devices = DS18B20()
count = devices.device_count()
names = devices.device_names()

print('[press ctrl+c to end the script]')
try: # Main program loop
	while True:
		i = 0
		print('\nReading temperature, number of sensors: {}'
							.format(count))

		while i < count:
			container = devices.tempC(i)
			print(container)
			#print (devices.tempC(0),devices.tempC(1))
			#print (container)
			"""
			print('{}. Temp: {:.3f}{}C, {:.3f}{}F of the device {}'
			  .format(i+1, container, degree_sign,
			  container * 9.0 / 5.0 + 32.0, degree_sign,names[i]))
			"""
			i = i + 1
	time.sleep(1)

# Scavenging work after the end of the program
except KeyboardInterrupt:
	print('Script end!')
