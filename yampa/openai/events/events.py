from pydantic import BaseModel

class Session(BaseModel):
    tools: list[str]

class SessionCreated(BaseModel):
    session : Session

def session_created_handler(event: str) -> SessionCreated:
    return SessionCreated.model_validate(event)
