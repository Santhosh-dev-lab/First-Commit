from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class UnitType(str, Enum):
    KG = "kg"
    TON = "ton"
    DAYS = "days"
    CELSIUS = "celsius"
    PERCENT = "percent"
    PPM = "ppm"
    LITER = "liter"


class TargetObjectiveType(str, Enum):
    YIELD = "yield"


class Objective(BaseModel):
    type: TargetObjectiveType
    target: float = Field(..., gt=0)
    unit: UnitType


class Deadline(BaseModel):
    value: float = Field(..., gt=0)
    unit: UnitType


class Crop(BaseModel):
    name: str
    variety: Optional[str] = None


class ResourceConstraint(BaseModel):
    resource_name: str
    max_amount: float
    unit: UnitType


class OptimizationObjective(str, Enum):
    MINIMIZE_WATER = "minimize_water"
    MINIMIZE_ENERGY = "minimize_energy"
    MAXIMIZE_YIELD = "maximize_yield"


class Zone(BaseModel):
    zone_id: str
    area_sqm: float = Field(..., gt=0)


class Sensor(BaseModel):
    sensor_id: str
    type: str
    zone_id: str


class Actuator(BaseModel):
    actuator_id: str
    type: str
    zone_id: str


class Polyhouse(BaseModel):
    polyhouse_id: str
    zones: List[Zone]
    sensors: List[Sensor]
    actuators: List[Actuator]


class Farm(BaseModel):
    farm_id: str
    location: str


class PhysicalIR(BaseModel):
    version: str = "0.1"
    farm: Farm
    polyhouse: Polyhouse
    crop: Crop
    objective: Objective
    deadline: Deadline
    optimization: List[OptimizationObjective] = []
    constraints: List[ResourceConstraint] = []
