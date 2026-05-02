from __future__ import annotations

from aiohttp import web


async def handle_healthz(_: web.Request) -> web.Response:
    return web.Response(text="ok\n", content_type="text/plain")
