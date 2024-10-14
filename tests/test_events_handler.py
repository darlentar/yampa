from pathlib import Path
import json

from yampa.openai.events import session_created_handler

def test_session_created():
    with open(Path(__file__).resolve().parent / Path("session_created.json")) as f:
        response = json.load(f)

    assert session_created_handler(response).session.tools == []

