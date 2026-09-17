from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any, Optional

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
    zones: Dict[str, Any]
    devices: Dict[str, Any]

class TwinCurrentState(BaseModel):
    timestamp: str
    environment: Dict[str, float]
    crop_biomass_kg: float
    substrate_moisture: float

class TwinPredictedState(BaseModel):
    forecast_horizon_days: float
    environment_forecast: Dict[str, float]
    predicted_yield_kg: float
    predicted_water_consumption_liters: float

class PolyhouseTwin(BaseModel):
    configuration: TwinConfiguration
    current_state: Optional[TwinCurrentState] = None
    predicted_state: Optional[TwinPredictedState] = None
    measurements: Dict[str, SensorReading] = {}
