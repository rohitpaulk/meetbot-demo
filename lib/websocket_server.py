from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from websockets.asyncio.server import Server, ServerConnection, serve

logger = logging.getLogger(__name__)


def _format_event(message: str | bytes) -> str:
    if isinstance(message, bytes):
        return f"<binary event: {len(message)} bytes>"

    try:
        parsed_message: Any = json.loads(message)
    except json.JSONDecodeError:
        return message

    return json.dumps(parsed_message, indent=2, sort_keys=True)


async def _handle_connection(websocket: ServerConnection) -> None:
    peer_name = websocket.remote_address
    print("Websocket client connected: %s", peer_name)

    try:
        async for message in websocket:
            print("Websocket event from %s:\n%s", peer_name, _format_event(message))
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
