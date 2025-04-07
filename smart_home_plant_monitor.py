import time
import grovepi
import math

# A port
LIGHT_SENSOR = 0
MOISTURE_SENSOR = 1

# D port
BUTTON_SENSOR = 2
TEMP_HUMIDITY_SENSOR = 3
RELAY_ACTUATOR = 4

# dht type
BLUE = 0
WHITE = 1

# relay state
RELAY_OFF = 0
RELAY_ON = 1

# button state
BUTTON_PRESSED = 1

# test timings
TIME_FOR_SENSOR = 4
TIME_TO_SLEEP = 1
WATERING_TIME = 5
MOISTURE_THRESHOLD = 80

# final timings
# TIME_FOR_SENSOR = 1 * 60 * 60
# TIME_TO_SLEEP = 1 * 60
# WATERING_TIME = 60
# MOISTURE_THRESHOLD = 18

# log file
LOG_FILE = "plant_monitor_log.csv"

def read_sensor():
    try:
        moisture = grovepi.analogRead(MOISTURE_SENSOR)
        light = grovepi.analogRead(LIGHT_SENSOR)
        button = grovepi.digitalRead(BUTTON_SENSOR)
        [temp, humidity] = grovepi.dht(TEMP_HUMIDITY_SENSOR, BLUE)
        if math.isnan(temp) or math.isnan(humidity):
            return [-1, -1, -1, -1]
        return [moisture, light, temp, humidity, button]

    except IOError as TypeError:
        return [-1, -1, -1, -1]


def init():
    grovepi.pinMode(LIGHT_SENSOR, "INPUT")
    grovepi.pinMode(MOISTURE_SENSOR, "INPUT")
    grovepi.pinMode(BUTTON_SENSOR, "INPUT")
    grovepi.pinMode(BUTTON_SENSOR, "INPUT")
    grovepi.pinMode(RELAY_ACTUATOR, "OUTPUT")
    print("Plant Monitor Started")
    with open(LOG_FILE, 'w') as f:
        f.write("time, moisture, light, temp, humidity, button, relay\n")

last_read_sensor = int(time.time())
init()
while True:
    curr_time_sec = int(time.time())
    relay = RELAY_OFF

    if curr_time_sec - last_read_sensor > TIME_FOR_SENSOR:
        [moisture, light, temp, humidity, button] = read_sensor()
        if moisture == -1:
            print("Bad reading")
            time.sleep(1)
            continue

        if (moisture != 0 and moisture < MOISTURE_THRESHOLD) or button == BUTTON_PRESSED:
            print("Relay On")
            relay = RELAY_ON
            grovepi.digitalWrite(RELAY_ACTUATOR, RELAY_ON)

        curr_time = time.strftime("%Y-%m-%d:%H-%M-%S")
        button_status = "Pressed" if button == BUTTON_PRESSED else "Not Pressed"
        relay_status = "On" if relay == RELAY_ON else "Off"
        print("Time: %s\nMoisture: %d\nLight: %d\nTemp: %.2f\nHumidity: %.2f %%\nButton: %s\nRelay: %s\n"
              % (curr_time, moisture, light, temp, humidity, button_status, relay_status))

        with open(LOG_FILE, 'a') as f:
            f.write("%s, %d, %d, %.2f, %.2f, %s, %s\n"
                    % (curr_time, moisture, light, temp, humidity, button_status, relay_status))

        if relay == RELAY_ON:
            time.sleep(WATERING_TIME)
            grovepi.digitalWrite(RELAY_ACTUATOR, RELAY_OFF)
            print("Relay Off")
            curr_time = time.strftime("%Y-%m-%d:%H-%M-%S")

        last_read_sensor = curr_time_sec

    time.sleep(TIME_TO_SLEEP)
