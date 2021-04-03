import time
from DS18B20classFile import DS18B20
# zum Testen der Temperatursensoren

degree_sign = u'\xb0' # degree sign
devices = DS18B20()
count = devices.device_count()
names = devices.device_names()

Klartext='xx' # Bezeichnung der Tempsensoren


print('[press ctrl+c to end the script]')
try: # Main program loop
	while True:
		i = 0
		print('\nReading temperature, number of sensors: {}'
							.format(count))

		while i < count:
			container = devices.tempC(i)
			if names[i]=='28-3c01d075619c':
				Klartext='Warmwasser'
			if names[i]=='28-3c01d075af0e':
				Klartext='P-Kalt'
			if names[i]=='28-3c01d075bdf3':
				Klartext='P-heiss'
			if names[i]=='28-012033389e18':
				Klartext='Raumtemperatur'
				
			if names[i]=='28-0120333b1a7b':
				Klartext='Puffer 1 von unten'

			if names[i]=='28-0120333abd5d':
				Klartext='Puffer 3 von unten'

			if names[i]=='28-0120333dff2b':
				Klartext='Puffer 2 von unten'

			if names[i]=='28-01203395e5cc':
				Klartext='Puffer 4 von unten'


			print(i," ",container,names[i],Klartext)
			#print (devices.tempC(0),devices.tempC(1))
			#print (container)
			"""
			print('{}. Temp: {:.3f}{}C, {:.3f}{}F of the device {}'
			  .format(i+1, container, degree_sign,
			  container * 9.0 / 5.0 + 32.0, degree_sign,names[i]))
			"""
			Klartext='xx'
			i = i + 1
		time.sleep(5)

# Scavenging work after the end of the program
except KeyboardInterrupt:
	print('Script end!')
