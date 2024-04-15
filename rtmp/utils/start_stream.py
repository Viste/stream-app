#!/bin/bash

COURSE_NAME=$1

RESPONSE=$(curl -s -X POST http://academy-service.stream.svc.pprfnk.local/api/start_broadcast \
     -H "Content-Type: application/json" \
     -d "{\"short_name\":\"$COURSE_NAME\"}")

echo $RESPONSE > "/home/response.log"

BROADCAST_ID=$(echo $RESPONSE | jq -r '.broadcast_id')

echo "BROADCAST ID: $BROADCAST_ID"

echo $BROADCAST_ID > "/home/${COURSE_NAME}_broadcast_id.txt"

