#!/bin/bash

PLANT_MONITOR_SCRIPT="plant_monitor.py"
WATER_SCRIPT="water.py"
AWS_PUBSUB_SCRIPT="aws_pubsub.py"

PYTHON2="python2"
PYTHON3="python3"

PLANT_MONITOR_PID="plant_monitor.pid"
WATER_PID="water.pid"
AWS_PUBSUB_PID="aws_pubsub.pid"

start_scripts() {
    if [ -f $PLANT_MONITOR_PID ] && kill -0 $(cat $PLANT_MONITOR_PID) 2>/dev/null; then
        echo "Error: $PLANT_MONITOR_SCRIPT is already running with PID $(cat $PLANT_MONITOR_PID)."
        exit 1
    fi

    if [ -f $WATER_PID ] && kill -0 $(cat $WATER_PID) 2>/dev/null; then
        echo "Error: $WATER_SCRIPT is already running with PID $(cat $WATER_PID)."
        exit 1
    fi

    if [ -f $AWS_PUBSUB_PID ] && kill -0 $(cat $AWS_PUBSUB_PID) 2>/dev/null; then
        echo "Error: $AWS_PUBSUB_SCRIPT is already running with PID $(cat $AWS_PUBSUB_PID)."
        exit 1
    fi

    echo "Starting scripts..."
    nohup $PYTHON2 $PLANT_MONITOR_SCRIPT > plant_monitor.log 2>&1 &
    echo $! > $PLANT_MONITOR_PID
    echo "Started $PLANT_MONITOR_SCRIPT with PID $(cat $PLANT_MONITOR_PID)"

    sleep 5

    nohup $PYTHON2 $WATER_SCRIPT > water.log 2>&1 &
    echo $! > $WATER_PID
    echo "Started $WATER_SCRIPT with PID $(cat $WATER_PID)"

    nohup $PYTHON3 $AWS_PUBSUB_SCRIPT > aws_pubsub.log 2>&1 &
    echo $! > $AWS_PUBSUB_PID
    echo "Started $AWS_PUBSUB_SCRIPT with PID $(cat $AWS_PUBSUB_PID)"
}

stop_scripts() {
    echo "Stopping scripts..."
    if [ -f $PLANT_MONITOR_PID ]; then
        kill $(cat $PLANT_MONITOR_PID) 2>/dev/null && echo "Stopped $PLANT_MONITOR_SCRIPT"
        rm -f $PLANT_MONITOR_PID
    fi

    if [ -f $WATER_PID ]; then
        kill $(cat $WATER_PID) 2>/dev/null && echo "Stopped $WATER_SCRIPT"
        rm -f $WATER_PID
    fi

    if [ -f $AWS_PUBSUB_PID ]; then
        kill $(cat $AWS_PUBSUB_PID) 2>/dev/null && echo "Stopped $AWS_PUBSUB_SCRIPT"
        rm -f $AWS_PUBSUB_PID
    fi
}

case "$1" in
    --end)
        stop_scripts
        ;;
    --rerun)
        stop_scripts
        start_scripts
        ;;
    *)
        start_scripts
        ;;
esac
