from __future__ import annotations

import os

import requests


def create_bot(meeting_url: str) -> None:
    response = requests.post(
        "https://us-west-2.recall.ai/api/v1/bot/",
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": os.environ["RECALL_AI_API_KEY"],
        },
        json={
            "meeting_url": meeting_url,
            "bot_name": "Meeting Notetaker",
            # "recording_config": {
            #     "realtime_endpoints": [
            #         {
            #             "type": "websocket",
            #             "url": "TODO",
            #             "events": [],
            #         }
            #     ]
            # },
        },
    )

    print(f"Bot creation response: {response.status_code} {response.text}")
