import asyncio
import websockets
import json

from .processors import EventHandler
from .events import make_conversation_item_create_event, make_session_update_event


class OpenAIRunner:
    def __init__(
        self,
        api_key: str,
        event_handler: EventHandler | None = None,
        tools: list | None = None,
    ):
        self.api_key = api_key
        self.event_handler = EventHandler() if event_handler is None else event_handler
        self.tools = [] if tools is None else tools
        self.create_event = asyncio.Queue()
        self.ws = None

    async def send_audio(self, audio: bytes):
        payload = make_conversation_item_create_event(audio)
        self.create_event.put_nowait(payload)

    async def stop_audio_send(self):
        await self.ws.close()

    async def run(self):
        url = (
            "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1",
        }
        self.ws = await websockets.connect(url, extra_headers=headers)
        if self.tools:
            event = make_session_update_event(tools=self.tools)
            await self.ws.send(event.json(exclude_none=True))

        async def handle_event(ws):
            async for message in ws:
                await self.event_handler.handle_event(json.loads(message))

        async def handle_audio_create(ws):
            while True:
                create_event = await self.create_event.get()
                await ws.send(create_event.json())
                await ws.send(json.dumps({"type": "response.create"}))

        async def handler(websocket):
            consumer_task = asyncio.create_task(handle_event(self.ws))
            producer_task = asyncio.create_task(handle_audio_create(self.ws))
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

        await handler(self.ws)
