from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aiohttp import web

from lib.openai_realtime import OUTPUT_SAMPLE_RATE, OpenAIRealtimeBridge, openai_realtime_bridge
from lib.server_app import get_camera_audio_clients, get_openai_bridge
from lib.server_endpoints.camera import handle_camera
from lib.server_endpoints.camera_audio import handle_camera_audio
from lib.server_endpoints.healthz import handle_healthz
from lib.server_endpoints.index import handle_index
from lib.server_endpoints.ws import handle_ws


async def _broadcast_openai_audio(app: web.Application) -> None:
    openai_bridge = get_openai_bridge(app)

    async for audio_base64 in openai_bridge.output_audio_chunks():
        message = json.dumps(
            {
                "type": "audio",
                "audio": audio_base64,
                "sampleRate": OUTPUT_SAMPLE_RATE,
            }
        )
        clients = get_camera_audio_clients(app)

        for websocket in tuple(clients):
            if websocket.closed:
                clients.discard(websocket)
                continue

            try:
                await websocket.send_str(message)
            except ConnectionResetError:
                clients.discard(websocket)


def _create_app(openai_bridge: OpenAIRealtimeBridge) -> web.Application:
    app = web.Application()
    app["openai_bridge"] = openai_bridge
    app["camera_audio_clients"] = set()
    app.router.add_get("/", handle_index)
    app.router.add_get("/healthz", handle_healthz)
    app.router.add_get("/camera", handle_camera)
    app.router.add_get("/camera-audio", handle_camera_audio)
    app.router.add_get("/ws", handle_ws)
    return app


@asynccontextmanager
async def server(host: str, port: int) -> AsyncGenerator[web.AppRunner]:
    async with openai_realtime_bridge() as openai_bridge:
        app = _create_app(openai_bridge)
        broadcast_task = asyncio.create_task(_broadcast_openai_audio(app))
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        try:
            print(f"Server listening on http://{host}:{port}")
            print(f"Camera page available at http://{host}:{port}/camera")
            print(f"Websocket endpoint available at ws://{host}:{port}/ws")
            yield runner
        finally:
            broadcast_task.cancel()
            try:
                await broadcast_task
            except asyncio.CancelledError:
                pass

            for websocket in tuple(get_camera_audio_clients(app)):
                await websocket.close()

            await runner.cleanup()
