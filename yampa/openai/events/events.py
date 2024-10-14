from pydantic import BaseModel
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
    description = tools[0].__doc__
    name = tools[0].__name__
    properties = {}
    required = []
    for p in inspect.signature(tools[0]).parameters.values():
        if p.annotation is str:
            property = {"type": "string"}
        elif get_origin(p.annotation) is Literal:
            property = {"type": "string", "enum": get_args(p.annotation)}
        else:
            raise NotImplementedError(f"annotation {p.annotation}")
        properties[p.name] = property
        required.append(p.name)

    parameters = {"type": "object", "properties": properties, "required": required}
    return SessionUpdate(
        type="session.update",
        session=Session(
            tools=[Tools(name=name, description=description, parameters=parameters)]
        ),
    )
