import csv
import time
import json
from awscrt import mqtt
from awsiot import mqtt_connection_builder

ENDPOINT = "a2953x3ipsvax0-ats.iot.ap-southeast-1.amazonaws.com"
CLIENT_ID = "basicPubSub"
TOPIC = "sdk/test/python"
PATH_TO_CERT = "raspberry_pi.cert.pem"
PATH_TO_KEY = "raspberry_pi.private.key"
PATH_TO_ROOT = "root-CA.crt"
CSV_FILE = "plant_monitor_log.csv"
TIME_TO_SLEEP = 1

def connect_to_aws():
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=PATH_TO_CERT,
        pri_key_filepath=PATH_TO_KEY,
        ca_filepath=PATH_TO_ROOT,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30)

    print("Connecting to AWS IoT...")
    try:
        connect_future = mqtt_connection.connect()
        connect_future.result()
        print("Connected!")
    except Exception as e:
        print(f"Failed to connect: {e}")
        exit(1)
    return mqtt_connection

def subscribe_to_topic(mqtt_connection):
    print("Subscribing to topic '{}'...".format(TOPIC))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=TOPIC,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=lambda topic, payload, **kwargs: print(f"Received message: {payload}")
    )
    subscribe_future.result()
    print("Subscribed!")

def construct_payload(line):
    return {
        "time": line[0],
        "environment": {
            "light": int(line[1]),
            "temperature": float(line[2]),
            "humidity": float(line[3])
        },
        "plants": [
            {
                "index": 1,
                "moisture": int(line[4]),
                "button": line[5],
                "relay": line[6]
            },
            {
                "index": 2,
                "moisture": int(line[7]),
                "button": line[8],
                "relay": line[9]
            }
        ]
    }

def clear_data(file_path, lines):
    if len(lines) > 50:
        with open(file_path, "w", newline="") as write_file:
            writer = csv.writer(write_file)
            writer.writerow(lines[0])
            writer.writerows(lines[-10:])

def read_last_line(file_path, last_time):
    with open(file_path, "r") as file:
        lines = list(csv.reader(file))

        if len(lines) > 1 and lines[-1][0] != last_time:
            clear_data(file_path, lines)
            return lines[-1]
        return None

mqtt_connection = connect_to_aws()
subscribe_to_topic(mqtt_connection)
last_time = None

while True:
    line = read_last_line(CSV_FILE, last_time)
    if line:
        payload = json.dumps(construct_payload(line))

        mqtt_connection.publish(
            topic = TOPIC,
            payload = payload,
            qos = mqtt.QoS.AT_LEAST_ONCE
        )
        last_time = line[0]
    time.sleep(TIME_TO_SLEEP)
