from pydantic import BaseModel
from typing import Literal


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
    turn_detection : None = None
    voice : Literal["alloy"]
