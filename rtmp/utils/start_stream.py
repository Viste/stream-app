#!/usr/bin/env python3
import sys
import requests
import json
import logging

logging.basicConfig(filename='/home/logfile.log', level=logging.DEBUG)


def start_stream(course_name):
    logging.debug("Starting stream for %s", course_name)
    url = "http://academy-service.stream.svc.pprfnk.local/api/start_broadcast"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"short_name": course_name})
    response = requests.post(url, headers=headers, data=data)
    broadcast_id = response.json().get('broadcast_id')

    with open(f"/home/{course_name}_broadcast_id.txt", "w") as f:
        f.write(str(broadcast_id))

    logging.debug("BROADCAST ID: %s", broadcast_id)
    logging.debug("Stream started for %s", course_name)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_stream(sys.argv[1])