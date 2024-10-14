from collections.abc import Awaitable
from .events import (
    conversation_item_created_event_handler,
    ConversationItem,
    AudioTranscriptDelta,
)


class FakeOpenAI:
    def __init__(
        self,
        events: list[str],
        on_item_created: Awaitable[[], [ConversationItem]] | None = None,
        on_transcript_delta: Awaitable[[], [AudioTranscriptDelta]] | None = None,
    ):
        self.events = events
        self.on_item_created = on_item_created
        self.on_transcript_delta = on_transcript_delta

    async def run(self):
        for event in self.events:
            if self.on_item_created and event["type"] == "conversation.item.created":
                item = conversation_item_created_event_handler(event)
                await self.on_item_created(item)
            if (
                self.on_transcript_delta
                and event["type"] == "response.audio_transcript.delta"
            ):
                item = AudioTranscriptDelta.model_validate(event)
                await self.on_transcript_delta(item)
