import time
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

def read_last_line(file_path, previous_line):
    with open(file_path, "r") as file:
        lines = file.readlines()
        if lines:
            last_line = lines[-1].strip()
            if last_line and last_line != previous_line:
                return last_line
        return None

def control_relay(relay_status, relay_actuator):
    relay = RELAY_ON if relay_status.strip().lower() == "on" else RELAY_OFF
    grovepi.digitalWrite(relay_actuator, relay)

last_line = None
while True:
    last_line = read_last_line(CSV_FILE, last_line)
    if last_line:
        log_time = last_line.split(",")[0]
        relay_1 = last_line.split(",")[6]
        relay_2 = last_line.split(",")[9]

        control_relay(relay_1, RELAY_ACTUATOR_1)
        control_relay(relay_2, RELAY_ACTUATOR_2)

        last_time = log_time

    time.sleep(TIME_TO_SLEEP)
