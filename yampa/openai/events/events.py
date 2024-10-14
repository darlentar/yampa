from pydantic import BaseModel
from pydub import AudioSegment
import io
import base64
from typing import Callable, Literal, get_origin, get_args
import inspect


class SessionParametersProperties(BaseModel):
    type: str
    enum: list[str] | None = None


class SessionParameters(BaseModel):
    type: str
    properties: dict[str, SessionParametersProperties]
    required: list[str]


class Tools(BaseModel):
    type: str = "function"
    name: str
    description: str
    parameters: SessionParameters


class Session(BaseModel):
    tools: list[Tools]


class SessionCreated(BaseModel):
    session: Session


class SessionUpdate(BaseModel):
    type: str
    session: Session


def session_created_handler(event: str) -> SessionCreated:
    return SessionCreated.model_validate(event)


def make_session_update_event(tools=list[Callable]) -> SessionUpdate:
    session_tools = []
    for tool in tools:
        description = tool.__doc__
        name = tool.__name__
        properties = {}
        required = []
        for p in inspect.signature(tool).parameters.values():
            if p.annotation is str:
                property = {"type": "string"}
            elif get_origin(p.annotation) is Literal:
                property = {"type": "string", "enum": get_args(p.annotation)}
            else:
                raise NotImplementedError(f"annotation: {p.annotation}")
            properties[p.name] = property
            # TODO: Support optional args
            required.append(p.name)

        parameters = {"type": "object", "properties": properties, "required": required}
        session_tools.append(
            Tools(name=name, description=description, parameters=parameters)
        )
    return SessionUpdate(
        type="session.update",
        session=Session(tools=session_tools),
    )


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
