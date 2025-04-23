import time
import grovepi
import math

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
TIME_FOR_SENSOR = 4
TIME_TO_SLEEP = 1
WATERING_TIME = 5
MOISTURE_THRESHOLD = 80

# final timings
# TIME_FOR_SENSOR = 1 * 60 * 60
# TIME_TO_SLEEP = 1
# WATERING_TIME = 60
# MOISTURE_THRESHOLD = 18

# log file
LOG_FILE = "plant_monitor_log.csv"

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

def get_relay_status(moisture, button):
    if (moisture != 0 and moisture < MOISTURE_THRESHOLD) or button == BUTTON_PRESSED:
        return "on"
    return "off"

def get_button_status(button):
    return "Pressed" if button == BUTTON_PRESSED else "Not Pressed"

last_read_sensor = int(time.time())
init()
while True:
    curr_time_sec = int(time.time())
    relay_1 = "off"
    relay_2 = "off"

    if curr_time_sec - last_read_sensor > TIME_FOR_SENSOR:
        [light, temp, humidity, moisture_1, button_1, moisture_2, button_2] = read_sensor()
        if moisture_1 == -1:
            print("Bad reading")
            time.sleep(1)
            continue

        curr_time = time.strftime("%Y-%m-%d:%H-%M-%S")

        relay_1 = get_relay_status(moisture_1, button_1)
        relay_2 = get_relay_status(moisture_2, button_2)

        button_status_1 = get_button_status(button_1)
        button_status_2 = get_button_status(button_2)

        with open(LOG_FILE, 'a') as f:
            f.write("%s, %d, %.2f, %.2f, %d, %s, %s, %d, %s, %s\n"
                    % (curr_time, light, temp, humidity, moisture_1, button_status_1, relay_1, moisture_2, button_status_2, relay_2))

        last_read_sensor = curr_time_sec

    time.sleep(TIME_TO_SLEEP)
