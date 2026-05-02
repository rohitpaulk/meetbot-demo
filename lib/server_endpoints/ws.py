from __future__ import annotations

from aiohttp import WSMsgType, web

from lib.events import AudioEvent, ChatMessageEvent, Event
from lib.server_app import get_openai_bridge


async def handle_ws(request: web.Request) -> web.WebSocketResponse:
    openai_bridge = get_openai_bridge(request.app)
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
