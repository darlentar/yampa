from pydantic import BaseModel


class AudioDelta(BaseModel):
    item_id: str
    delta: str
