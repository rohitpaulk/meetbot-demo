from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


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
        }.get(parsed_message.get("event"), Event)

        return klass(type=parsed_message["event"], data=parsed_message.get("data", {}))

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
    def buffer_base64(self) -> str:
        return self.data["data"]["buffer"]
