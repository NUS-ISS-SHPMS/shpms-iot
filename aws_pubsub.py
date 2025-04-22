import csv
import time
import os
from awscrt import mqtt
from awsiot import mqtt_connection_builder
import logging

logging.basicConfig(level=logging.DEBUG)

ENDPOINT = "a2953x3ipsvax0-ats.iot.ap-southeast-1.amazonaws.com"
CLIENT_ID = "basicPubSub"
TOPIC = "sdk/test/python"
PATH_TO_CERT = "raspberry_pi.cert.pem"
PATH_TO_KEY = "raspberry_pi.private.key"
PATH_TO_ROOT = "root-CA.crt"
CSV_FILE = "plant_monitor_log.csv"


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

# Subscribe to a test topic
print("Subscribing to topic '{}'...".format(TOPIC))
subscribe_future, packet_id = mqtt_connection.subscribe(
    topic=TOPIC,
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=lambda topic, payload, **kwargs: print(f"Received message: {payload}")
)
subscribe_future.result()
print("Subscribed!")

last_sent_line = ""

def read_last_line(filename):
    if not os.path.exists(filename):
        return ""
    with open(filename, "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            return ""
        return lines[-1].strip()

while True:
    line = read_last_line(CSV_FILE)
    if line and line != last_sent_line:
        print("Publishing:", line)
        mqtt_connection.publish(
            topic=TOPIC,
            payload=line,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        last_sent_line = line
    time.sleep(5)
