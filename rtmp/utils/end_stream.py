#!/usr/bin/env python3
import sys
import requests
import json
import subprocess


def convert_flv_to_mp4(flv_path, mp4_path):
    command = ['ffmpeg', '-i', flv_path, '-codec', 'copy', mp4_path]
    subprocess.run(command, check=True)


def end_stream(course_name):
    with open(f"/home/{course_name}_broadcast_id.txt", "r") as f:
        broadcast_id = f.read().strip()

    base_video_path = f"/home/storage/{course_name}.flv"

    # Конвертация в MP4
    unique_video_name_mp4 = f"{course_name}_{broadcast_id}.mp4"
    unique_video_path_mp4 = f"/home/storage/{unique_video_name_mp4}"
    convert_flv_to_mp4(base_video_path, unique_video_path_mp4)

    url = "https://academy.pprfnk.tech/api/end_broadcast"
    headers = {"Content-Type": "application/json", "X-API-Key": "pprfkebetvsehrot2024"}
    data = json.dumps({"broadcast_id": broadcast_id, "video_path": unique_video_name_mp4})
    requests.post(url, headers=headers, data=data)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        end_stream(sys.argv[1])