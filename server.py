import asyncio
import json
import os
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from yampa.openai.processors import EventHandler
from yampa.openai.runner import OpenAIRunner
from yampa.openai.events import AudioTranscriptDone
from yampa.openai.events import OutputItemDone

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    def get_product_remmaining_stock(product_id: int) -> int:
        """Get product remaining given an id."""
        try:
            return [1, 23, 244, 344, 123][product_id]
        except IndexError:
            return 0

    async def on_transcript_delta_done(audio_transcript: AudioTranscriptDone):
        await websocket.send_json(
            {
                "type": "new.transcript",
                "data": audio_transcript.transcript,
            }
        )

    openai_runner = OpenAIRunner(
        api_key=os.getenv("OPENAI_API_KEY"),
        tools=[get_product_remmaining_stock],
    )

    async def on_output_item_done(output_item: OutputItemDone):
        if output_item.item.name == "get_product_remmaining_stock":
            params = json.loads(output_item.item.arguments)
            result = get_product_remmaining_stock(**params)
            send_json = json.dumps(
                {
                    "type": "conversation.item.create",
                    "item": {
                        "call_id": output_item.item.call_id,
                        "type": "function_call_output",
                        # "role": "system",
                        "output": str(result),
                    },
                }
            )
            print("SendJSON", send_json)
            await openai_runner.ws.send(send_json)
            await openai_runner.ws.send(json.dumps({"type": "response.create"}))

    event_handler = EventHandler(
        on_transcript_delta_done=on_transcript_delta_done,
        on_output_item_done=on_output_item_done,
    )
    # TODO: add a setter
    openai_runner.event_handler = event_handler
    await websocket.accept()
    asyncio.create_task(openai_runner.run())
    while True:
        data = await websocket.receive()
        await openai_runner.send_audio(data["bytes"])
    openai_runner.stop_audio_send()
