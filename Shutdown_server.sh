#!/bin/bash

# Trova il processo associato a server.py
process_info=$(ps aux | grep server.py | grep -v grep)

# Controlla se il processo è stato trovato
if [ -n "$process_info" ]; then
    # Estrai il PID dal risultato
    pid=$(echo "$process_info" | awk '{print $2}')

    # Termina il processo
    kill "$pid"
    echo "Il processo server.py con PID $pid è stato terminato."
else
    echo "Il processo server.py non è stato trovato in esecuzione."
fi