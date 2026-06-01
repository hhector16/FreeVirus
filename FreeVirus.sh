#!/bin/bash

LOG_FILE="logs.log"

sudo pkill -f motor.py
sudo pkill -f av_fanotify
sudo pkill -f antivirusUI.py



gcc av_fanotify.c -o av_fanotify 

if [ $? -ne 0 ]; then
    exit 1
fi

sudo python3 antivirusUI.py >> $LOG_FILE 2>&1 &

sleep 5

sudo python3 motor.py >> $LOG_FILE 2>&1 &

sleep 2

sudo ./av_fanotify >> $LOG_FILE 2>&1

