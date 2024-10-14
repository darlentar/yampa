from pydantic import BaseModel


class ConversationItemCreated(BaseModel):
    event_id: str


def conversation_item_created_event_handler(event: str) -> ConversationItemCreated:
    return ConversationItemCreated.model_validate(event)
