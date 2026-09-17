from enum import Enum

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


class CropCategory(str, Enum):
    DWARF = "dwarf"
    STANDARD = "standard"


class Crop(BaseModel):
    name: str
    category: CropCategory | None = None
    variety: str | None = None
    plant_density_per_sqm: float | None = None


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
    zones: list[Zone]
    sensors: list[Sensor]
    actuators: list[Actuator]


class Farm(BaseModel):
    farm_id: str
    location: str


class HarvestStateEnum(str, Enum):
    NOT_READY = "NOT_READY"
    DEVELOPING = "DEVELOPING"
    READY = "READY"
    OVERDUE = "OVERDUE"


class HarvestObjective(BaseModel):
    target_state: HarvestStateEnum


class VisionConfig(BaseModel):
    enabled: bool = False


class PhysicalIR(BaseModel):
    version: str = "0.1"
    farm: Farm
    polyhouse: Polyhouse
    crop: Crop
    objective: Objective
    deadline: Deadline
    optimization: list[OptimizationObjective] = []
    constraints: list[ResourceConstraint] = []
    vision: VisionConfig | None = None
    harvest: HarvestObjective | None = None
