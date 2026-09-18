from enum import Enum
from typing import Any

from pydantic import BaseModel

from domains.polyhouse.engine import ZoneSimConfig


class ClockMode(str, Enum):
    REALTIME = "REALTIME"
    ACCELERATED = "ACCELERATED"
    STEP = "STEP"

class RuntimeStatus(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"

class ScenarioType(str, Enum):
    NORMAL = "NORMAL"
    WATER_SHORTAGE = "WATER_SHORTAGE"
    HEAT_WAVE = "HEAT_WAVE"
    HIGH_HUMIDITY = "HIGH_HUMIDITY"
    LOW_TEMPERATURE = "LOW_TEMPERATURE"
    LOW_TANK = "LOW_TANK"
    SENSOR_FAILURE = "SENSOR_FAILURE"
    GATEWAY_OFFLINE = "GATEWAY_OFFLINE"
    PUMP_FAILURE = "PUMP_FAILURE"
    VALVE_FAILURE = "VALVE_FAILURE"
    NETWORK_LATENCY = "NETWORK_LATENCY"
    PACKET_LOSS = "PACKET_LOSS"

class VirtualSensorConfig(BaseModel):
    sensor_id: str
    zone_id: str | None = None
    sensor_type: str
    unit: str
    noise_mode: str = "NONE" # NONE, GAUSSIAN, BIAS, DRIFT
    failure_mode: str = "ONLINE" # ONLINE, OFFLINE, STALE, BIASED, DRIFTING
    bias_value: float = 0.0
    noise_std: float = 0.0

class VirtualActuatorConfig(BaseModel):
    actuator_id: str
    zone_id: str | None = None
    actuator_type: str

class VirtualFarmRuntimeConfig(BaseModel):
    run_id: str
    farm_id: str
    clock_mode: ClockMode
    step_size_hours: float = 1.0
    zones: list[ZoneSimConfig]
    scenario: ScenarioType = ScenarioType.NORMAL
    seed: int = 42
    sensors: list[VirtualSensorConfig] = []
    actuators: list[VirtualActuatorConfig] = []
    initial_temperature_c: float = 23.0
    initial_humidity_percent: float = 70.0
    initial_co2_ppm: float = 800.0
    initial_par_umol_m2_s: float = 350.0
    outside_temperature_c: float = 18.0
    outside_humidity_percent: float = 60.0

class RuntimeStatusResponse(BaseModel):
    run_id: str
    farm_id: str
    status: RuntimeStatus
    simulation_time: float
    scenario: ScenarioType
    clock_mode: ClockMode
    current_step: int
    last_telemetry_timestamp: float | None = None
    gateway_status: str
    sensor_summary: dict[str, Any]
    actuator_summary: dict[str, Any]
    failure_summary: list[str]
