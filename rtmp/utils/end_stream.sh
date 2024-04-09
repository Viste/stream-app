#!/bin/bash

COURSE_NAME=$1

# ID трансляции из файла
BROADCAST_ID=$(cat "/home/${COURSE_NAME}_broadcast_id.txt")

# добавляем ID трансляции к имени файла
UNIQUE_VIDEO_PATH="/home/storage/${COURSE_NAME}_${BROADCAST_ID}.mp4"

# копируем то что высрал nginx в уникальный айдишник
cp "/home/storage/${COURSE_NAME}.mp4" "$UNIQUE_VIDEO_PATH"

# Обновляем информацию о трансляции с новым путем к видео
curl -X POST http://academy-service.stream.svc.pprfnk.local/api/end_broadcast \
     -H "Content-Type: application/json" \
     -d "{\"broadcast_id\":$BROADCAST_ID, \"video_path\":\"$UNIQUE_VIDEO_PATH\"}"