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

# dht type
blue=0
white=1

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
		[temp,humidity] = grovepi.dht(temp_himidity_sensor,blue)
		if math.isnan(temp) or math.isnan(humidity):
			return [-1,-1,-1,-1]
		return [moisture,light,temp,humidity]

	except IOError as TypeError:
			return [-1,-1,-1,-1]

last_read_sensor= int(time.time())

while True:
	curr_time_sec=int(time.time())

	if curr_time_sec-last_read_sensor>time_for_sensor:
		[moisture,light,temp,humidity]=read_sensor()
		if moisture==-1:
			print("Bad reading")
			time.sleep(1)
			continue

		curr_time = time.strftime("%Y-%m-%d:%H-%M-%S")
		print(("Time:%s\nMoisture: %d\nLight: %d\nTemp: %.2f\nHumidity:%.2f %%\n" %(curr_time,moisture,light,temp,humidity)))

		f=open(log_file,'a')
		f.write("%s,%d,%d,%.2f,%.2f;\n" %(curr_time,moisture,light,temp,humidity))
		f.close()

		last_read_sensor=curr_time_sec

	time.sleep(time_to_sleep)
