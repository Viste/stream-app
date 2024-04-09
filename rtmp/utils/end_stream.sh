#!/bin/bash

COURSE_NAME=$1
VIDEO_PATH="/home/storage/${COURSE_NAME}.mp4"

# Обновляем путь к видео
curl -X POST http://academy-service.stream.svc.pprfnk.local/api/update_video_path \
     -H "Content-Type: application/json" \
     -d "{\"short_name\":\"$COURSE_NAME\", \"video_path\":\"$VIDEO_PATH\"}"

# Обновляем статус is_live на false
curl -X POST http://academy-service.stream.svc.pprfnk.local/api/update_status \
     -H "Content-Type: application/json" \
     -d "{\"short_name\":\"$COURSE_NAME\", \"is_live\":false}"