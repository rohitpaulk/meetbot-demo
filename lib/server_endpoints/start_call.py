from __future__ import annotations

from aiohttp import web

from lib.server_app import set_call_started


async def handle_start_call(request: web.Request) -> web.Response:
    set_call_started(request.app, True)
    raise web.HTTPSeeOther("/")
