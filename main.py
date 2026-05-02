from __future__ import annotations

import asyncio

from dotenv import load_dotenv

from lib.google import create_meet
from lib.recall import create_bot


async def main() -> None:
    load_dotenv()

    # meeting_url, space_name = _create_meet()

    meeting_url = "https://meet.google.com/non-sdhm-att"
    space_name = "spaces/ZMTxRI7eHe0B"

    print(f"Space created: {meeting_url}")
    print(f"Space resource: {space_name}")

    create_bot(meeting_url)


if __name__ == "__main__":
    asyncio.run(main())
