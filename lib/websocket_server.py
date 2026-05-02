from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from websockets.asyncio.server import Server, ServerConnection, serve

logger = logging.getLogger(__name__)


@dataclass
class Event:
    type: str
    data: dict[str, Any]

    @classmethod
    def from_message(cls, message: str | bytes) -> Event | None:
        if isinstance(message, bytes):
            print("Received binary message instead of event: %d bytes", len(message))
            return None

        try:
            parsed_message: Any = json.loads(message)
        except json.JSONDecodeError:
            print(f"<non-JSON event: {len(message)} chars>")
            return Event(type="unknown", data={"raw": message})

        klass = {
            "participant_events.chat_message": ChatMessageEvent,
            "audio_mixed_raw.data": AudioEvent,
        }.get(parsed_message.get("type"), Event)

        return klass(type=parsed_message["type"], data=parsed_message.get("data", {}))

    def is_chat_message(self) -> bool:
        return self.type == "participant_events.chat_message"

    def is_audio(self) -> bool:
        return self.type == "audio_mixed_raw.data"

    def __repr__(self) -> str:
        return f"Event({self.type})"


class ChatMessageEvent(Event):
    def participant_name(self) -> str | None:
        return self.data["data"]["participant"]["name"]

    def message_text(self) -> str | None:
        return self.data["data"]["data"]["text"]


class AudioEvent(Event):
    pass


async def _handle_connection(websocket: ServerConnection) -> None:
    peer_name = websocket.remote_address
    print("Websocket client connected: %s", peer_name)

    try:
        async for message in websocket:
            event = Event.from_message(message)

            if not event:
                print("Receive invalid payload")
                continue

            if event.is_audio():
                print(".", end="", flush=True)
            elif event.is_chat_message():
                assert isinstance(event, ChatMessageEvent)
                print("Chat message from %s: %s", event.participant_name(), event.message_text())
            else:
                print("Unknown event from %s:%s", peer_name, print(repr(message)))

    except Exception:
        print("Websocket connection failed: %s", peer_name)
        raise
    finally:
        print("Websocket client disconnected: %s", peer_name)


@asynccontextmanager
async def websocket_server(host: str, port: int) -> AsyncGenerator[Server]:
    async with serve(_handle_connection, host, port) as server:
        print("Websocket server listening on ws://%s:%s", host, port)
        yield server
