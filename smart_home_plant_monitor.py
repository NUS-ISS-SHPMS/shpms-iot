import time
import grovepi
import math

# A port
light_sensor = 0
mositure_sensor = 1

# D port
button_sensor = 2
temp_himidity_sensor = 3
relay_actuator = 4

grovepi.pinMode(light_sensor, "INPUT")
grovepi.pinMode(mositure_sensor, "INPUT")
grovepi.pinMode(button_sensor, "INPUT")
grovepi.pinMode(button_sensor, "INPUT")
grovepi.pinMode(relay_actuator, "OUTPUT")

# dht type
blue = 0
white = 1

# relay state
relay_off = 0
relay_on = 1

# button state
button_pressed = 1

# test timings
time_for_sensor = 4
time_to_sleep = 1
watering_time = 5
moisture_threshold = 80
# final timings
# time_for_sensor = 1 * 60 * 60
# time_to_sleep = 1 * 60
# watering_time = 60
# moisture_threshold = 18

log_file = "plant_monitor_log.csv"

def read_sensor():
    try:
        moisture = grovepi.analogRead(mositure_sensor)
        light = grovepi.analogRead(light_sensor)
        button = grovepi.digitalRead(button_sensor)
        [temp, humidity] = grovepi.dht(temp_himidity_sensor, blue)
        if math.isnan(temp) or math.isnan(humidity):
            return [-1, -1, -1, -1]
        return [moisture, light, temp, humidity, button]

    except IOError as TypeError:
        return [-1, -1, -1, -1]

last_read_sensor = int(time.time())

print("Plant Monitor Started")
with open(log_file, 'w') as f:
	f.write("time, moisture, light, temp, humidity, button, relay\n")

while True:
    curr_time_sec = int(time.time())
    relay = relay_off

    if curr_time_sec - last_read_sensor > time_for_sensor:
        [moisture, light, temp, humidity, button] = read_sensor()
        if moisture == -1:
            print("Bad reading")
            time.sleep(1)
            continue

        if (moisture != 0 and moisture < moisture_threshold) or button == button_pressed:
          print("Relay On")
          relay = relay_on
          grovepi.digitalWrite(relay_actuator, relay_on)

        curr_time = time.strftime("%Y-%m-%d:%H-%M-%S")
        button_status = "Pressed" if button == button_pressed else "Not Pressed"
        relay_status = "On" if relay == relay_on else "Off"
        print("Time: %s\nMoisture: %d\nLight: %d\nTemp: %.2f\nHumidity: %.2f %%\nButton: %s\nRelay: %s\n"
              %(curr_time, moisture, light, temp, humidity, button_status, relay_status))

        with open(log_file, 'a') as f:
          f.write("%s, %d, %d, %.2f, %.2f, %s, %s\n"
                  %(curr_time, moisture, light, temp, humidity, button_status, relay_status))

        if relay == relay_on:
          time.sleep(watering_time)
          grovepi.digitalWrite(relay_actuator, relay_off)
          print("Relay Off")
          curr_time = time.strftime("%Y-%m-%d:%H-%M-%S")

        last_read_sensor = curr_time_sec

    time.sleep(time_to_sleep)
