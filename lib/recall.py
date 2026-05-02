from __future__ import annotations

import os

import requests


def create_bot(meeting_url: str, websocket_url: str) -> str:
    response = requests.post(
        _build_url("api/v1/bot"),
        headers=_default_headers(),
        json={
            "meeting_url": meeting_url,
            "bot_name": "Andy (CodeCrafters)",
            "recording_config": {
                "audio_mixed_raw": {},
                "realtime_endpoints": [
                    {
                        "type": "websocket",
                        "url": websocket_url,
                        "events": [
                            "participant_events.chat_message",
                            "audio_mixed_raw.data",
                        ],
                    }
                ],
            },
        },
    )

    print(f"Bot creation response: {response.status_code} {response.text}")
    response.raise_for_status()

    return response.json()["id"]


def enable_camera(bot_id: str, camera_url: str) -> None:
    response = requests.post(
        _build_url(f"api/v1/bot/{bot_id}/output_media/"),
        headers=_default_headers(),
        json={
            "camera": {"kind": "webpage", "config": {"url": camera_url}},
        },
    )

    print(f"Enabled camera response: {response.status_code} {response.text}")
    response.raise_for_status()


def _build_url(path: str) -> str:
    if path.startswith("/"):
        path = path[1:]

    return f"https://us-west-2.recall.ai/{path}"


def _default_headers() -> dict[str, str]:
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": os.environ["RECALL_AI_API_KEY"],
    }
