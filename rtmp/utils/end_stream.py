#!/usr/bin/env python3
import sys
import requests
import json
import shutil


def end_stream(course_name):
    with open(f"/home/{course_name}_broadcast_id.txt", "r") as f:
        broadcast_id = f.read().strip()

    unique_video_name = f"{course_name}_{broadcast_id}.flv"
    unique_video_path = f"/home/storage/{unique_video_name}"
    shutil.copy(f"/home/storage/{course_name}.flv", unique_video_path)

    url = "https://academy.pprfnk.tech/api/end_broadcast"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"broadcast_id": broadcast_id, "video_path": unique_video_name})
    requests.post(url, headers=headers, data=data)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        end_stream(sys.argv[1])