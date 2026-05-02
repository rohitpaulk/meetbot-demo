from __future__ import annotations

import asyncio
import logging

from dotenv import load_dotenv

from lib.google import create_meet
from lib.recall import create_bot, enable_camera
from lib.websocket_server import websocket_server


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    async with websocket_server("localhost", 8765):
        # meeting_url, space_name = _create_meet()

        meeting_url = "https://meet.google.com/non-sdhm-att"
        space_name = "spaces/ZMTxRI7eHe0B"

        print(f"Space created: {meeting_url}")
        print(f"Space resource: {space_name}")

        bot_id = create_bot(meeting_url, "wss://meetbot.ngrok.io")

        input("Bot joined. Press Enter to enable camera...")
        enable_camera(bot_id, "https://ccbench.org/")

        # Keep alive so we can keep getting events
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
