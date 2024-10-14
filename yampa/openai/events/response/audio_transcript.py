from pydantic import BaseModel


class AudioTranscriptDelta(BaseModel):
    item_id: str
    delta: str
