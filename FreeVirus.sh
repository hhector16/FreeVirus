#!/bin/bash

LOG_FILE="logs.log"

# 🔴 matar procesos anteriores primero
echo " Cerrando procesos antiguos..." | tee -a $LOG_FILE
sudo pkill -f motor.py
sudo pkill -f av_fanotify
sudo pkill -f antivirusUI.py

# Crear archivo de logs automáticamente
touch $LOG_FILE

echo "==============================" > $LOG_FILE
echo " FreeVirus Logs $(date)" >> $LOG_FILE
echo "==============================" >> $LOG_FILE

echo " Iniciando FreeVirus..." | tee -a $LOG_FILE

echo " Compilando av_fanotify.c..." | tee -a $LOG_FILE

gcc av_fanotify.c -o av_fanotify >> $LOG_FILE 2>&1

if [ $? -ne 0 ]; then
    echo " Error compilando av_fanotify.c" | tee -a $LOG_FILE
    exit 1
fi

echo " Compilación completada" | tee -a $LOG_FILE

echo " Iniciando interfaz gráfica..." | tee -a $LOG_FILE
sudo python3 antivirusUI.py >> $LOG_FILE 2>&1 &

sleep 5

echo " Iniciando motor.py..." | tee -a $LOG_FILE
sudo python3 motor.py >> $LOG_FILE 2>&1 &

sleep 2

echo " Ejecutando av_fanotify..." | tee -a $LOG_FILE
sudo ./av_fanotify >> $LOG_FILE 2>&1

echo " FreeVirus finalizado" | tee -a $LOG_FILE
