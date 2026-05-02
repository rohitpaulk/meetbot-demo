from __future__ import annotations

import asyncio
import os
from urllib.parse import urlparse, urlunparse

from aiohttp import web

from lib.recall import create_bot
from lib.server_app import get_call_started, set_bot_id
from lib.server_endpoints.index import MEETING_URL, render_index


def _websocket_url() -> str:
    public_base_url = os.environ["PUBLIC_BASE_URL"].rstrip("/")
    parsed_url = urlparse(public_base_url)
    scheme = "wss" if parsed_url.scheme == "https" else "ws"
    return urlunparse(parsed_url._replace(scheme=scheme, path="/ws", params="", query="", fragment=""))


def _add_bot() -> str:
    return create_bot(MEETING_URL, _websocket_url())


async def handle_add_bot(request: web.Request) -> web.Response:
    try:
        bot_id = await asyncio.to_thread(_add_bot)
    except Exception as error:
        print(f"Failed to add bot: {error}")
        return render_index(
            status_message=f"Failed to add bot: {error}",
            status_kind="error",
            call_started=get_call_started(request.app),
        )

    set_bot_id(request.app, bot_id)
    print(f"Bot added: {bot_id}")
    return render_index(
        status_message=f"Bot added successfully: {bot_id}. Wait for it to join, then enable camera.",
        status_kind="success",
        bot_id=bot_id,
        call_started=get_call_started(request.app),
    )
