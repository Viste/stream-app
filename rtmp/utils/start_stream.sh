#!/bin/bash

COURSE_NAME=$1

# Запускаем новую трансляцию и получаем её ID
BROADCAST_ID=$(curl -s -X POST http://academy-service.stream.svc.pprfnk.local/api/start_broadcast \
     -H "Content-Type: application/json" \
     -d "{\"short_name\":\"$COURSE_NAME\"}" | jq -r '.broadcast_id')

# Сохраняем ID трансляции для использования в end_stream.sh
echo $BROADCAST_ID > "/home/${COURSE_NAME}_broadcast_id.txt"