from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from aiohttp import WSMsgType, web
from jinja2 import Environment, FileSystemLoader, select_autoescape

from lib.events import AudioEvent, ChatMessageEvent, Event
from lib.openai_realtime import OpenAIRealtimeBridge, openai_realtime_bridge

IMAGE_URL = "https://ca.slack-edge.com/T02UQK7R1QC-U07H9ETQW67-fa8609795b2b-512"
MUSIC_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
TEMPLATES_DIR = Path(__file__).parent / "templates"

_jinja = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(("html", "jinja")),
)


async def _handle_websocket(request: web.Request) -> web.WebSocketResponse:
    openai_bridge = _get_openai_bridge(request.app)
    websocket = web.WebSocketResponse()
    await websocket.prepare(request)

    peer_name = request.remote
    print(f"Websocket client connected: {peer_name}")

    try:
        async for message in websocket:
            if message.type == WSMsgType.TEXT:
                event = Event.from_message(message.data)
            elif message.type == WSMsgType.BINARY:
                event = Event.from_message(message.data)
            elif message.type == WSMsgType.ERROR:
                print(f"Websocket connection failed: {peer_name}: {websocket.exception()}")
                break
            else:
                continue

            if not event:
                print("Receive invalid payload")
                continue

            if event.is_audio():
                assert isinstance(event, AudioEvent)
                await openai_bridge.send_input_audio(event.buffer_base64())
            elif event.is_chat_message():
                assert isinstance(event, ChatMessageEvent)
                print(f"Chat message from {event.participant_name()}: {event.message_text()}")
            else:
                print(f"Unknown event from {peer_name}: {message.data!r}")
    finally:
        print(f"Websocket client disconnected: {peer_name}")

    return websocket


async def _handle_camera(_: web.Request) -> web.Response:
    template = _jinja.get_template("camera.html.jinja")
    html = template.render(
        title="Meetbot Video",
        image_url=IMAGE_URL,
        image_alt="Meetbot avatar",
        caption="Meetbot is here.",
        music_url=MUSIC_URL,
        music_volume=0.35,
    )

    return web.Response(text=html, content_type="text/html")


async def _handle_index(_: web.Request) -> web.Response:
    return web.Response(
        text=(
            "Meetbot server is running.\n\n"
            "Endpoints:\n"
            "- GET /camera: camera webpage\n"
            "- GET /healthz: health check\n"
            "- WS /ws: Recall realtime events\n"
        ),
        content_type="text/plain",
    )


async def _handle_healthz(_: web.Request) -> web.Response:
    return web.Response(text="ok\n", content_type="text/plain")


def _get_openai_bridge(app: web.Application) -> OpenAIRealtimeBridge:
    bridge = app["openai_bridge"]
    assert isinstance(bridge, OpenAIRealtimeBridge)
    return bridge


def _create_app(openai_bridge: OpenAIRealtimeBridge) -> web.Application:
    app = web.Application()
    app["openai_bridge"] = openai_bridge
    app.router.add_get("/", _handle_index)
    app.router.add_get("/healthz", _handle_healthz)
    app.router.add_get("/camera", _handle_camera)
    app.router.add_get("/ws", _handle_websocket)
    return app


@asynccontextmanager
async def bot_server(host: str, port: int) -> AsyncGenerator[web.AppRunner]:
    async with openai_realtime_bridge() as openai_bridge:
        app = _create_app(openai_bridge)
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        try:
            print(f"Bot server listening on http://{host}:{port}")
            print(f"Camera page available at http://{host}:{port}/camera")
            print(f"Websocket endpoint available at ws://{host}:{port}/ws")
            yield runner
        finally:
            await runner.cleanup()
