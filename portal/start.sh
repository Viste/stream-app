#!/bin/bash

# Запуск сервера Node.js в фоне
node server.js &

# Запуск Gunicorn на переднем плане
exec gunicorn -b 0.0.0.0:5000 -w 8 main:app