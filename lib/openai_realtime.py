from __future__ import annotations

import asyncio
import base64
import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import numpy as np
import numpy.typing as npt
import soxr
from openai import AsyncOpenAI
from openai.resources.realtime.realtime import AsyncRealtimeConnection

MODEL = "gpt-realtime-1.5"
VOICE = "ash"
RECALL_INPUT_SAMPLE_RATE = 16_000
OPENAI_SAMPLE_RATE = 24_000
OUTPUT_SAMPLE_RATE = OPENAI_SAMPLE_RATE

INSTRUCTIONS = (
    "You are a concise, helpful product demo assistant in a live Google Meet call. "
    "Always speak in English, even if you are unsure what language the user is speaking. "
    "Speak naturally and keep responses brief."
)


def _resample_recall_audio_to_openai(audio_base64: str) -> str:
    if RECALL_INPUT_SAMPLE_RATE == OPENAI_SAMPLE_RATE:
        return audio_base64

    recall_audio = base64.b64decode(audio_base64)
    recall_samples = np.frombuffer(recall_audio, dtype=np.dtype("<i2")).astype(np.float32) / 32768.0
    openai_samples = soxr.resample(recall_samples, RECALL_INPUT_SAMPLE_RATE, OPENAI_SAMPLE_RATE)
    openai_audio = _float32_to_pcm16(openai_samples)
    return base64.b64encode(openai_audio).decode("ascii")


def _float32_to_pcm16(samples: npt.NDArray[np.float32]) -> bytes:
    clipped_samples = np.clip(samples, -1.0, 1.0)
    pcm16_samples = (clipped_samples * 32767.0).astype(np.dtype("<i2"))
    return pcm16_samples.tobytes()


class OpenAIRealtimeBridge:
    def __init__(self, connection: AsyncRealtimeConnection) -> None:
        self._connection = connection
        self._output_audio_queue: asyncio.Queue[str] = asyncio.Queue(maxsize=200)
        self._reader_task = asyncio.create_task(self._read_events())

    async def start(self) -> None:
        await self._send_event(
            {
                "type": "session.update",
                "session": {
                    "type": "realtime",
                    "model": MODEL,
                    "output_modalities": ["audio"],
                    "audio": {
                        "input": {
                            "format": {
                                "type": "audio/pcm",
                                "rate": OPENAI_SAMPLE_RATE,
                            },
                            "turn_detection": {
                                "type": "semantic_vad",
                            },
                        },
                        "output": {
                            "format": {
                                "type": "audio/pcm",
                                "rate": OPENAI_SAMPLE_RATE,
                            },
                            "voice": VOICE,
                        },
                    },
                    "instructions": INSTRUCTIONS,
                },
            }
        )

    async def stop(self) -> None:
        self._reader_task.cancel()
        try:
            await self._reader_task
        except asyncio.CancelledError:
            pass

        await self._connection.close()

    async def send_input_audio(self, audio_base64: str) -> None:
        await self._send_event(
            {
                "type": "input_audio_buffer.append",
                "audio": _resample_recall_audio_to_openai(audio_base64),
            }
        )

    async def output_audio_chunks(self) -> AsyncGenerator[str]:
        while True:
            yield await self._output_audio_queue.get()

    async def _send_event(self, event: dict[str, object]) -> None:
        await self._connection.send_raw(json.dumps(event))

    async def _read_events(self) -> None:
        while True:
            event = await self._connection.recv()
            event_type = getattr(event, "type", None)

            if event_type not in {"response.output_audio.delta", "response.audio.delta", "error"}:
                continue

            if event_type == "error":
                print(f"OpenAI realtime error: {event}")
                continue

            delta = getattr(event, "delta", None)
            if not isinstance(delta, str):
                continue

            try:
                self._output_audio_queue.put_nowait(delta)
            except asyncio.QueueFull:
                _ = self._output_audio_queue.get_nowait()
                self._output_audio_queue.put_nowait(delta)


@asynccontextmanager
async def openai_realtime_bridge() -> AsyncGenerator[OpenAIRealtimeBridge]:
    client = AsyncOpenAI()

    async with client.realtime.connect(model=MODEL) as connection:
        bridge = OpenAIRealtimeBridge(connection)
        await bridge.start()
        try:
            yield bridge
        finally:
            await bridge.stop()
