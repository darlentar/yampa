from pathlib import Path
from typing import Literal
import json

from yampa.openai.events import session_created_handler, make_session_update_event


def test_session_created():
    with open(Path(__file__).resolve().parent / Path("session_created.json")) as f:
        response = json.load(f)

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
