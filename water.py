import time
import csv
import grovepi

# D port
RELAY_ACTUATOR_1 = 4
RELAY_ACTUATOR_2 = 8

# relay state
RELAY_OFF = 0
RELAY_ON = 1

TIME_TO_SLEEP = 1
CSV_FILE = "plant_monitor_log.csv"

grovepi.pinMode(RELAY_ACTUATOR_1, "OUTPUT")
grovepi.pinMode(RELAY_ACTUATOR_2, "OUTPUT")


def read_last_line(file_path, last_time):
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        lines = list(reader)
        if len(lines) > 1 and lines[-1][0] != last_time:
            return lines[-1]
        return None

def control_relay(relay_status, relay_actuator):
  relay = RELAY_ON if relay_status.strip().lower() == "on" else RELAY_OFF
  grovepi.digitalWrite(relay_actuator, relay)

last_time = None
while True:
    last_line = read_last_line(CSV_FILE, last_time)
    if last_line:
        log_time = last_line[0]
        relay_1 = last_line[6]
        relay_2 = last_line[9]

        control_relay(relay_1, RELAY_ACTUATOR_1)
        control_relay(relay_2, RELAY_ACTUATOR_2)

        last_time = log_time
    time.sleep(TIME_TO_SLEEP)
