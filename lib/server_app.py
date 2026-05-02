from __future__ import annotations

from aiohttp import web

from lib.openai_realtime import OpenAIRealtimeBridge


def get_openai_bridge(app: web.Application) -> OpenAIRealtimeBridge:
    bridge = app["openai_bridge"]
    assert isinstance(bridge, OpenAIRealtimeBridge)
    return bridge


def get_camera_audio_clients(app: web.Application) -> set[web.WebSocketResponse]:
    clients = app["camera_audio_clients"]
    assert isinstance(clients, set)
    return clients


def get_bot_id(app: web.Application) -> str | None:
    bot_id = app["bot_id"]
    assert isinstance(bot_id, str) or bot_id is None
    return bot_id


def set_bot_id(app: web.Application, bot_id: str) -> None:
    app["bot_id"] = bot_id
