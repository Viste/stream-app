#!/bin/bash

echo "Running database migrations..."
flask db upgrade

echo "Running node server for player..."
node server.js &

echo "Running node server for player..."
exec gunicorn -b 0.0.0.0:5000 -w 32 main:app