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


def get_call_started(app: web.Application) -> bool:
    call_started = app["call_started"]
    assert isinstance(call_started, bool)
    return call_started


def set_call_started(app: web.Application, call_started: bool) -> None:
    app["call_started"] = call_started


def get_camera_enabled(app: web.Application) -> bool:
    camera_enabled = app["camera_enabled"]
    assert isinstance(camera_enabled, bool)
    return camera_enabled


def set_camera_enabled(app: web.Application, camera_enabled: bool) -> None:
    app["camera_enabled"] = camera_enabled
