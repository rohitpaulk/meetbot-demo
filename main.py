from __future__ import annotations

import asyncio

from dotenv import load_dotenv

from lib.server import server


async def main() -> None:
    load_dotenv()

    async with server("0.0.0.0", 8765):
        # Keep alive so we can keep getting events
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
