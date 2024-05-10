import json
import logging
import os
import sys

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests

logging.basicConfig(filename='/home/logfile.log', level=logging.DEBUG)

scopes = ["https://www.googleapis.com/auth/youtube"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"


def create_youtube_broadcast_and_stream(title, description):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    # Создание объекта трансляции
    insert_broadcast_response = youtube.liveBroadcasts().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "scheduledStartTime": "2023-01-30T00:00:00.000Z"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    ).execute()

    broadcast_id = insert_broadcast_response["id"]

    # Создание объекта потока
    insert_stream_response = youtube.liveStreams().insert(
        part="snippet,cdn",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "cdn": {
                "format": "1080p",
                "ingestionType": "rtmp"
            }
        }
    ).execute()

    stream_id = insert_stream_response["id"]

    # Связывание трансляции и потока
    bind_broadcast_response = youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast_id,
        streamId=stream_id
    ).execute()

    return broadcast_id, stream_id


def start_stream(course_name):
    logging.debug("Starting stream for %s", course_name)
    url = "https://academy.pprfnk.tech/api/start_broadcast"
    headers = {"Content-Type": "application/json", "X-API-Key": "pprfkebetvsehrot2024"}
    data = json.dumps({"short_name": course_name})
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()
    broadcast_id = response_data.get('broadcast_id')
    title = response_data.get('title')

    with open(f"/home/{course_name}_broadcast_id.txt", "w") as f:
        f.write(str(broadcast_id))

    logging.debug("BROADCAST ID: %s", broadcast_id)
    logging.debug("Stream started for %s with title %s", course_name, title)

   # youtube_description = "Описание трансляции"
   # youtube_broadcast_id, youtube_stream_id = create_youtube_broadcast_and_stream(title, youtube_description)
    logging.debug("YouTube Broadcast ID: %s, Stream ID: %s", youtube_broadcast_id, youtube_stream_id)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_stream(sys.argv[1])
