from enum import Enum
from typing import Any

from pydantic import BaseModel


class SensorQuality(str, Enum):
    GOOD = "GOOD"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    INVALID = "INVALID"
    MISSING = "MISSING"


class StateSource(str, Enum):
    OBSERVED = "OBSERVED"
    ESTIMATED = "ESTIMATED"
    PREDICTED = "PREDICTED"
    SIMULATED = "SIMULATED"
    CONFIGURED = "CONFIGURED"
    CALIBRATED = "CALIBRATED"


class StateVariable(BaseModel):
    value: float
    unit: str
    source: StateSource


class SensorReading(BaseModel):
    value: float
    unit: str
    timestamp: float
    quality: SensorQuality


class TwinConfiguration(BaseModel):
    polyhouse_id: str
    zones: dict[str, Any]
    devices: dict[str, Any]


class TwinCurrentState(BaseModel):
    timestamp: float
    environment: dict[str, StateVariable]
    crop_biomass_kg: StateVariable
    substrate_moisture: StateVariable
    tank_volume: StateVariable | None = None


class TwinPredictedState(BaseModel):
    forecast_horizon_days: float
    environment_forecast: dict[str, StateVariable]
    predicted_yield_kg: StateVariable
    predicted_water_consumption_liters: StateVariable


class PolyhouseTwin(BaseModel):
    configuration: TwinConfiguration
    current_state: TwinCurrentState | None = None
    predicted_state: TwinPredictedState | None = None
    measurements: dict[str, SensorReading] = {}

