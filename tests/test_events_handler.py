import pytest
from pathlib import Path
from typing import Literal, Any
import json

from yampa.openai.events import (
    conversation_item_created_event_handler,
    session_created_handler,
    make_session_update_event,
    make_conversation_item_create_event,
)


@pytest.fixture
def get_json():
    def _get_json(path: Path | str) -> Any:
        with open(Path(__file__).resolve().parent / path) as f:
            return json.load(f)

    return _get_json


@pytest.fixture
def get_audio():
    def _get_audio(path: Path | str) -> bytes:
        with open(Path(__file__).resolve().parent / path, "rb") as f:
            return f.read()

    return _get_audio


def test_session_created(get_json):
    response = get_json("session_created.json")
    assert session_created_handler(response).session.tools == []


def test_make_session_update_event():
    def get_weather(location: str, scale: Literal["C", "F", "K"]) -> str:
        """Get the weather at a given location."""
        pass

    assert make_session_update_event(tools=[get_weather]).model_dump(
        exclude_none=True
    ) == {
        "type": "session.update",
        "session": {
            "tools": [
                {
                    "type": "function",
                    "name": "get_weather",
                    "description": "Get the weather at a given location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "scale": {"type": "string", "enum": ["C", "F", "K"]},
                        },
                        "required": ["location", "scale"],
                    },
                }
            ]
        },
    }


# TODO: make custom assert to avoid long diff with audio bytes
def test_make_conversation_item_create_event(get_audio, get_json):
    response = get_json("conversation_item_create.json")
    audio = get_audio("ask_orders.m4a")
    assert make_conversation_item_create_event(audio=audio).model_dump(exclude_none=True) == response


def test_make_conversation_item_created_event(get_audio, get_json):
    response = get_json("conversation_item_created.json")
    assert (
        conversation_item_created_event_handler(response).event_id
        == "event_AIJUPO0vK28UCZ9EwV9dD"
    )
