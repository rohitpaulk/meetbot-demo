from __future__ import annotations

import asyncio
import os

from aiohttp import web

from lib.recall import enable_camera
from lib.server_app import get_bot_id, get_call_started, set_camera_enabled
from lib.server_endpoints.index import render_index


def _camera_url() -> str:
    return f"{os.environ['PUBLIC_BASE_URL'].rstrip('/')}/camera"


async def handle_enable_camera(request: web.Request) -> web.Response:
    bot_id = get_bot_id(request.app)

    if bot_id is None:
        return render_index(
            status_message="Add a bot before enabling camera.",
            status_kind="error",
            call_started=get_call_started(request.app),
        )

    try:
        await asyncio.to_thread(enable_camera, bot_id, _camera_url())
    except Exception as error:
        print(f"Failed to enable camera for bot {bot_id}: {error}")
        return render_index(
            status_message=f"Failed to enable camera: {error}",
            status_kind="error",
            bot_id=bot_id,
            call_started=get_call_started(request.app),
        )

    set_camera_enabled(request.app, True)
    print(f"Camera enabled for bot: {bot_id}")
    return render_index(
        status_message=f"Camera enabled for bot: {bot_id}",
        status_kind="success",
        bot_id=bot_id,
        call_started=get_call_started(request.app),
        camera_enabled=True,
    )
