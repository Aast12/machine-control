from dataclasses import dataclass
from app.core.state import MachineState
from enum import Enum
import typing


class MessageType(str, Enum):
    UPDATE_STATE = "update"
    ERROR = "error"


class ErrorBody(typing.TypedDict):
    message: str


class ReceiveUpdateBody(typing.TypedDict):
    original_state: MachineState
    new_state: MachineState


@dataclass
class ErrorMessage:
    data: ErrorBody
    type: typing.Literal[MessageType.ERROR] = MessageType.ERROR


@dataclass
class SendUpdateMessage:
    data: MachineState
    last_temp_update: float
    type: typing.Literal[MessageType.UPDATE_STATE] = MessageType.UPDATE_STATE


OutMessage = SendUpdateMessage | ErrorMessage


@dataclass
class ReceiveUpdateMessage:
    type: typing.Literal[MessageType.UPDATE_STATE]
    data: ReceiveUpdateBody


InMessage = ReceiveUpdateMessage


def parse_receive_update(message: dict[str, typing.Any]) -> ReceiveUpdateMessage:
    """Parse and validate an incoming update message from a client.
    Raises ValueError if message type is not present, or not an update
    Raises TypeError if keys are missing or types are wrong
    """
    if "type" not in message or message["type"] != MessageType.UPDATE_STATE.value:
        raise ValueError("Invalid message type")

    # raises TypeError if keys are missing or types are wrong
    return ReceiveUpdateMessage(**message)
