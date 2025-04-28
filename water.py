from enum import Enum
from datetime import datetime
import time
import json
import grovepi

class Source(Enum):
    LOCAL = "local"
    REMOTE = "remote"

# D port
RELAY_ACTUATOR_1 = 4
RELAY_ACTUATOR_2 = 8

# relay state
RELAY_OFF = 0
RELAY_ON = 1

TIME_TO_SLEEP = 1
CSV_FILE = "plant_monitor_log.csv"
REMOTE_FILE = "remote.ndjson"

grovepi.pinMode(RELAY_ACTUATOR_1, "OUTPUT")
grovepi.pinMode(RELAY_ACTUATOR_2, "OUTPUT")

relay_block_time = {
    RELAY_ACTUATOR_1: 0,
    RELAY_ACTUATOR_2: 0
}

def read_last_line(file_path, previous_line):
    with open(file_path, "r") as file:
        lines = file.readlines()
        if lines:
            last_line = lines[-1].strip()
            if last_line and last_line != previous_line:
                return last_line
        return None

def control_relay(relay_status, relay_actuator, log_time, source):
    print("log time2: ", log_time)
    if isinstance(log_time, str):
        log_time = time.mktime(datetime.strptime(log_time, "%Y-%m-%d:%H-%M-%S").timetuple())

    if source == Source.LOCAL and log_time < relay_block_time[relay_actuator]:
        return

    relay = RELAY_ON if relay_status.strip().lower() == "on" else RELAY_OFF
    grovepi.digitalWrite(relay_actuator, relay)

    relay_block_time[relay_actuator] = log_time + 60

def process_remote_command(log_time):
    try:
        with open(REMOTE_FILE, "r+") as file:
            lines = file.readlines()
            if lines:
                first_line = lines[0].strip()
                json_data = json.loads(first_line)

                actuator = json_data.get("actuator")
                state = json_data.get("state")

                if actuator in ["relay1", "relay2"] and state in ["on", "off"]:
                    relay_actuator = RELAY_ACTUATOR_1 if actuator == "relay1" else RELAY_ACTUATOR_2
                    control_relay(state, relay_actuator, log_time, Source.REMOTE)

                file.seek(0)
                file.writelines(lines[1:])
                file.truncate()

    except Exception as e:
        print("Error processing remote command: {}".format(e))

last_line = None
while True:
    last_line = read_last_line(CSV_FILE, last_line)
    if last_line:
        log_time = last_line.split(",")[0]
        relay_1 = last_line.split(",")[6]
        relay_2 = last_line.split(",")[9]

        control_relay(relay_1, RELAY_ACTUATOR_1, log_time, Source.LOCAL)
        control_relay(relay_2, RELAY_ACTUATOR_2, log_time, Source.LOCAL)

        last_time = log_time

    process_remote_command(log_time)

    time.sleep(TIME_TO_SLEEP)
