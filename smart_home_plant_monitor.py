import time
import grovepi
import math

# A port
light_sensor			= 0
mositure_sensor = 1

# D port
button_sensor = 2
temp_himidity_sensor	= 3
relay = 4

grovepi.pinMode(light_sensor,"INPUT")
grovepi.pinMode(mositure_sensor,"INPUT")
grovepi.pinMode(button_sensor,"INPUT")
grovepi.pinMode(button_sensor,"INPUT")
grovepi.pinMode(relay,"OUTPUT")

# dht type
blue=0
white=1

# relay state
relay_off=0
relay_on=1

#test timings
time_for_sensor		= 4
time_to_sleep		= 1
#	final timings
# time_for_sensor		= 1*60*60
# time_to_sleep		= 1*60

log_file="plant_monitor_log.csv"

def read_sensor():
	try:
		moisture=grovepi.analogRead(mositure_sensor)
		light=grovepi.analogRead(light_sensor)
		button=grovepi.digitalRead(button_sensor)
		[temp,humidity] = grovepi.dht(temp_himidity_sensor,blue)
		if math.isnan(temp) or math.isnan(humidity):
			return [-1,-1,-1,-1]
		return [moisture,light,temp,humidity,button]

	except IOError as TypeError:
			return [-1,-1,-1,-1]

last_read_sensor= int(time.time())

print("Plant Monitor Started")
while True:
	curr_time_sec=int(time.time())
	relay_status = relay_off

	if curr_time_sec-last_read_sensor>time_for_sensor:
		[moisture,light,temp,humidity,button]=read_sensor()
		if moisture==-1:
			print("Bad reading")
			time.sleep(1)
			continue

		curr_time = time.strftime("%Y-%m-%d:%H-%M-%S")
		button_status = "Pressed" if button == 1 else "Not Pressed"
		print("Time:%s\nMoisture: %d\nLight: %d\nTemp: %.2f\nHumidity:%.2f %%\nButton: %s\nRelay: %s\n" %(curr_time,moisture,light,temp,humidity,button_status,relay_status))

		f=open(log_file,'a')
		f.write("%s,%d,%d,%.2f,%.2f,%s,%s;\n" %(curr_time,moisture,light,temp,humidity,button_status,relay_status))
		f.close()

		# grovepi.digitalWrite(relay,relay_on)
		# relay_status = relay_on

		last_read_sensor=curr_time_sec

	time.sleep(time_to_sleep)
