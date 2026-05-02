from __future__ import annotations

import asyncio

from aiohttp import web

from lib.recall import create_bot, enable_camera
from lib.server_endpoints.index import MEETING_URL, render_index

WEBSOCKET_URL = "wss://meetbot.ngrok.io/ws"
CAMERA_URL = "https://meetbot.ngrok.io/camera"


def _add_bot() -> str:
    bot_id = create_bot(MEETING_URL, WEBSOCKET_URL)
    enable_camera(bot_id, CAMERA_URL)
    return bot_id


async def handle_add_bot(_: web.Request) -> web.Response:
    try:
        bot_id = await asyncio.to_thread(_add_bot)
    except Exception as error:
        print(f"Failed to add bot: {error}")
        return render_index(
            status_message=f"Failed to add bot: {error}",
            status_kind="error",
        )

    print(f"Bot added: {bot_id}")
    return render_index(
        status_message=f"Bot added successfully: {bot_id}",
        status_kind="success",
    )
