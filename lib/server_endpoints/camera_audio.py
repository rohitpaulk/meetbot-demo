from __future__ import annotations

from aiohttp import WSMsgType, web

from lib.server_app import get_camera_audio_clients


async def handle_camera_audio(request: web.Request) -> web.WebSocketResponse:
    websocket = web.WebSocketResponse()
    await websocket.prepare(request)

    clients = get_camera_audio_clients(request.app)
    clients.add(websocket)

    peer_name = request.remote
    print(f"Camera audio client connected: {peer_name}")

    try:
        async for message in websocket:
            if message.type == WSMsgType.ERROR:
                print(f"Camera audio websocket failed: {peer_name}: {websocket.exception()}")
                break
    finally:
        clients.discard(websocket)
        print(f"Camera audio client disconnected: {peer_name}")

    return websocket
