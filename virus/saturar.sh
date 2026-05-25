#!/bin/bash

echo "▲ Compilando saturar.c..."

gcc ./virus/saturar.c -o ./virus/saturar

# Verificar compilación
if [ $? -ne 0 ]; then
    echo "❌ Error compilando saturar.c"
    exit 1
fi

echo "✅ Compilación completada"

./virus/saturar
