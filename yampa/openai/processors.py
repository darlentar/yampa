from collections.abc import Awaitable
from .events import conversation_item_created_event_handler, ConversationItem

class FakeOpenAI():
    def __init__(self, events:list[str], on_item_created: Awaitable[[], [ConversationItem]],):
        self.events = events
        self.on_item_created = on_item_created
        
    async def run(self):
        for event in self.events:
            if event["type"] == "conversation.item.created":
                item = conversation_item_created_event_handler(event)
                await self.on_item_created(item)