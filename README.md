# README

## Preparation

1. **Download AWS IoT Core Certificates**
  Go to AWS IoT Core and download the following files:
  - `root-CA.crt`
  - `raspberry_pi.private.key`
  - `raspberry_pi.cert.pem`
  After downloading, use `chmod` to set the correct permissions for these files. For example:
  ```bash
  chmod 600 root-CA.crt raspberry_pi.private.key raspberry_pi.cert.pem
  ```

2. **Create Empty Log Files**
  Create two empty files in the project directory:
  - `plant_monitor_log.csv`
  - `mqtt_log.txt`
  You can create them using the `touch` command:
  ```bash
  touch plant_monitor_log.csv mqtt_log.txt
  ```

3. **Set Permissions for `run.sh`**
  Use `chmod` to set the correct permissions for the `run.sh` script:
  ```bash
  chmod +x run.sh
  ```

## Running the Script

The `run.sh` script supports three parameters:
1. `start` - Starts the monitoring process.
2. `stop` - Stops the monitoring process.
3. `status` - Displays the current status of the monitoring process.

Example usage:
```bash
./run.sh start
```

## Python Scripts Overview

1. **`sensor_monitor.py`**
  This script collects data from the sensors and logs it into `plant_monitor_log.csv`.

2. **`mqtt_client.py`**
  This script handles MQTT communication, sending sensor data to AWS IoT Core and logging messages to `mqtt_log.txt`.

3. **`data_analyzer.py`**
  This script analyzes the logged sensor data and provides insights or alerts based on predefined thresholds.
