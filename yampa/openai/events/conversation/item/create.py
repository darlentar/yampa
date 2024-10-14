from pydantic import BaseModel
from pydub import AudioSegment
import io
import base64


def audio_to_item_create_event(audio_bytes: bytes) -> str:
    # Load the audio file from the byte stream
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

    # Resample to 24kHz mono pcm16
    pcm_audio = audio.set_frame_rate(24000).set_channels(1).set_sample_width(2).raw_data

    # Encode to base64 string
    return base64.b64encode(pcm_audio).decode()


# TODO: Support other types than audio
class ConversationItemContent(BaseModel):
    type: str = "input_audio"
    audio: str


class ConversationItem(BaseModel):
    type: str = "message"
    role: str = "user"
    content: list[ConversationItemContent]


class ConversationItemCreate(BaseModel):
    type: str = "conversation.item.create"
    item: ConversationItem


def make_conversation_item_create_event(audio: bytes) -> ConversationItemCreate:
    return ConversationItemCreate(
        item=ConversationItem(
            content=[ConversationItemContent(audio=audio_to_item_create_event(audio))],
        ),
    )
