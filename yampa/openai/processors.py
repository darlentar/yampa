from collections.abc import Awaitable
from .events import (
    conversation_item_created_event_handler,
    ConversationItem,
    AudioDelta,
    AudioDone,
    AudioTranscriptDelta,
    AudioTranscriptDone,
)


class FakeOpenAI:
    def __init__(
        self,
        events: list[str],
        on_item_created: Awaitable[[], [ConversationItem]] | None = None,
        on_transcript_delta: Awaitable[[], [AudioTranscriptDelta]] | None = None,
        on_transcript_delta_done: Awaitable[[], [AudioTranscriptDone]] | None = None,
        on_audio_delta: Awaitable[[], [AudioDelta]] | None = None,
        on_audio_done: Awaitable[[], [AudioDone]] | None = None,
    ):
        self.events = events
        self.on_item_created = on_item_created
        self.on_transcript_delta = on_transcript_delta
        self.on_transcript_delta_done = on_transcript_delta_done
        self.on_audio_delta = on_audio_delta
        self.on_audio_done = on_audio_done

    async def run(self):
        for event in self.events:
            if self.on_item_created and event["type"] == "conversation.item.created":
                item = conversation_item_created_event_handler(event)
                await self.on_item_created(item)
            elif (
                self.on_transcript_delta
                and event["type"] == "response.audio_transcript.delta"
            ):
                item = AudioTranscriptDelta.model_validate(event)
                await self.on_transcript_delta(item)
            elif (
                self.on_transcript_delta_done
                and event["type"] == "response.audio_transcript.done"
            ):
                item = AudioTranscriptDone.model_validate(event)
                await self.on_transcript_delta_done(item)
            elif self.on_audio_delta and event["type"] == "response.audio.delta":
                item = AudioDelta.model_validate(event)
                await self.on_audio_delta(item)
            elif self.on_audio_done and event["type"] == "response.audio.done":
                item = AudioDone.model_validate(event)
                await self.on_audio_done(item)
