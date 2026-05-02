from __future__ import annotations

from aiohttp import web


async def handle_index(_: web.Request) -> web.Response:
    return web.Response(
        text=(
            "Meetbot server is running.\n\n"
            "Endpoints:\n"
            "- GET /camera: camera webpage\n"
            "- GET /healthz: health check\n"
            "- WS /camera-audio: streamed bot audio for camera page\n"
            "- WS /ws: Recall realtime events\n"
        ),
        content_type="text/plain",
    )
