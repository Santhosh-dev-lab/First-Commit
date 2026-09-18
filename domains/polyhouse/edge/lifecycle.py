from enum import Enum

from pydantic import BaseModel

from .gateway import EdgeCommand


class CommandStatus(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    SENT = "SENT"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    TIMEOUT = "TIMEOUT"


class CommandLifecycle(BaseModel):
    command_id: str
    status: CommandStatus = CommandStatus.CREATED
    command: EdgeCommand
    reason: str = ""
    timestamp_updated: float
