from enum import Enum
from typing import Any

from pydantic import BaseModel


class SensorQuality(str, Enum):
    GOOD = "GOOD"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    INVALID = "INVALID"
    MISSING = "MISSING"

class SensorReading(BaseModel):
    value: float
    unit: str
    timestamp: str
    quality: SensorQuality

class TwinConfiguration(BaseModel):
    polyhouse_id: str
    zones: dict[str, Any]
    devices: dict[str, Any]

class TwinCurrentState(BaseModel):
    timestamp: str
    environment: dict[str, float]
    crop_biomass_kg: float
    substrate_moisture: float

class TwinPredictedState(BaseModel):
    forecast_horizon_days: float
    environment_forecast: dict[str, float]
    predicted_yield_kg: float
    predicted_water_consumption_liters: float

class PolyhouseTwin(BaseModel):
    configuration: TwinConfiguration
    current_state: TwinCurrentState | None = None
    predicted_state: TwinPredictedState | None = None
    measurements: dict[str, SensorReading] = {}
