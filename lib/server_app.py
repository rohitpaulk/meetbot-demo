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
