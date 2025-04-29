import time
import grovepi
import math
from enum import Enum
import json
from datetime import datetime

# A port
LIGHT_SENSOR = 0
MOISTURE_SENSOR_2 = 1
MOISTURE_SENSOR_1 = 2

# D port
TEMP_HUMIDITY_SENSOR = 2
BUTTON_SENSOR_1 = 3
BUTTON_SENSOR_2 = 7

# dht type
BLUE = 0
WHITE = 1

# button state
BUTTON_PRESSED = 1

# test timings
TIME_FOR_SENSOR = 1
TIME_TO_SLEEP = 1
MOISTURE_THRESHOLD = 80
REMOTE_WATERING_TIME = 60

# final timings
# TIME_FOR_SENSOR = 1
# TIME_TO_SLEEP = 1
# MOISTURE_THRESHOLD = 180
# REMOTE_WATERING_TIME = 60

# log file
LOG_FILE = "plant_monitor_log.csv"
REMOTE_FILE = "remote.ndjson"

relay_block_time = {
    "relay1": None,
    "relay2": None
}

def process_remote_command(start_time):
    with open(REMOTE_FILE, "r+") as file:
        lines = file.readlines()
        if lines:
            first_line = lines[0].strip()
            json_data = json.loads(first_line)

            actuator = json_data.get("actuator")
            state = json_data.get("state")

            if actuator in ["relay1", "relay2"] and state in ["on", "off"]:
                relay_block_time[actuator] = (convert_time(start_time) + REMOTE_WATERING_TIME, state)

            file.seek(0)
            file.writelines(lines[1:])
            file.truncate()

def read_sensor():
    try:
        light = grovepi.analogRead(LIGHT_SENSOR)
        [temp, humidity] = grovepi.dht(TEMP_HUMIDITY_SENSOR, BLUE)

        moisture_1 = grovepi.analogRead(MOISTURE_SENSOR_1)
        button_1 = grovepi.digitalRead(BUTTON_SENSOR_1)


        moisture_2 = grovepi.analogRead(MOISTURE_SENSOR_2)
        button_2 = grovepi.digitalRead(BUTTON_SENSOR_2)

        if math.isnan(temp) or math.isnan(humidity):
            return [-1, -1, -1, -1, -1, -1, -1]
        return [light, temp, humidity, moisture_1, button_1, moisture_2, button_2]

    except IOError as TypeError:
        return [-1, -1, -1, -1, -1, -1, -1]

def convert_time(time_str):
    return time.mktime(datetime.strptime(time_str, "%Y-%m-%d:%H-%M-%S").timetuple())

def init():
    grovepi.pinMode(LIGHT_SENSOR, "INPUT")
    grovepi.pinMode(TEMP_HUMIDITY_SENSOR, "INPUT")
    grovepi.pinMode(MOISTURE_SENSOR_1, "INPUT")
    grovepi.pinMode(BUTTON_SENSOR_1, "INPUT")
    grovepi.pinMode(MOISTURE_SENSOR_2, "INPUT")
    grovepi.pinMode(BUTTON_SENSOR_2, "INPUT")

    print("Plant Monitor Started")
    with open(LOG_FILE, 'w') as f:
        f.write("time, light, temp, humidity, moisture_1, button_1, relay_1, moisture_2, button_2, relay_2\n")

def get_relay_status(relay, moisture, button, curr_time):
    if relay_block_time[relay]:
        end_time, state = relay_block_time[relay]
        if convert_time(curr_time) < end_time:
            return state
        else:
            relay_block_time[relay] = None

    if (moisture > 5 and moisture < MOISTURE_THRESHOLD) or button == BUTTON_PRESSED:
        return "on"
    return "off"

def get_button_status(button):
    return "Pressed" if button == BUTTON_PRESSED else "Not Pressed"

init()
while True:
    relay_1 = "off"
    relay_2 = "off"

    [light, temp, humidity, moisture_1, button_1, moisture_2, button_2] = read_sensor()
    if moisture_1 == -1:
        print("Bad reading")
        time.sleep(TIME_TO_SLEEP)
        continue

    curr_time = time.strftime("%Y-%m-%d:%H-%M-%S")
    process_remote_command(curr_time)

    relay_1 = get_relay_status("relay1", moisture_1, button_1, curr_time)
    relay_2 = get_relay_status("relay2", moisture_2, button_2, curr_time)

    button_status_1 = get_button_status(button_1)
    button_status_2 = get_button_status(button_2)

    with open(LOG_FILE, 'a') as f:
        f.write("%s, %d, %.2f, %.2f, %d, %s, %s, %d, %s, %s\n"
                % (curr_time, light, temp, humidity, moisture_1, button_status_1, relay_1, moisture_2, button_status_2, relay_2))

    time.sleep(TIME_TO_SLEEP)
