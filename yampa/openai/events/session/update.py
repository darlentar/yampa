from typing import Callable
from .base import Session, Tools
from pydantic import BaseModel
import inspect
from typing import Literal, get_origin, get_args


class SessionUpdate(BaseModel):
    type: str
    session: Session


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
