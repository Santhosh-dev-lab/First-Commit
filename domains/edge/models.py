from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TelemetrySource(str, Enum):
    LOCAL_SIMULATION = "LOCAL_SIMULATION"
    EDGE_GATEWAY = "EDGE_GATEWAY"
    AWS_IOT = "AWS_IOT"


class TelemetryEnvelope(BaseModel):
    farm_id: str
    gateway_id: str
    device_id: str
    zone_id: str | None = None
    timestamp: float
    sequence_number: int | None = None
    schema_version: str = "1.0"
    source: TelemetrySource
    measurements: dict[str, float] = Field(default_factory=dict)
    firmware_version: str | None = None
    metadata: dict[str, Any] | None = None


class CommandType(str, Enum):
    PUMP_ON = "PUMP_ON"
    PUMP_OFF = "PUMP_OFF"
    VALVE_OPEN = "VALVE_OPEN"
    VALVE_CLOSE = "VALVE_CLOSE"
    VENT_OPEN = "VENT_OPEN"
    VENT_CLOSE = "VENT_CLOSE"

class CommandEnvelope(BaseModel):
    command_id: str = Field(min_length=1, max_length=100)
    farm_id: str = Field(min_length=1, max_length=100)
    gateway_id: str = Field(min_length=1, max_length=100)
    device_id: str = Field(min_length=1, max_length=100)
    timestamp: float
    command_type: CommandType
    parameters: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = "1.0"


class GatewayHeartbeat(BaseModel):
    gateway_id: str
    farm_id: str
    timestamp: float
    status: str
    firmware_version: str | None = None
