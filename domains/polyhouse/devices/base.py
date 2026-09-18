"""
domains/polyhouse/devices/base.py

Generic Sensor and Actuator contracts for PHYSICA.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from twin.core import SensorQuality


class SensorFailureMode(BaseModel):
    mode: str = "NORMAL"  # NORMAL, MISSING, STALE, BIAS, NOISE, OUT_OF_RANGE, INTERMITTENT
    bias_value: float = 0.0
    noise_std: float = 0.0


class Sensor(ABC):
    def __init__(self, sensor_id: str, zone_id: str, sensor_type: str, unit: str):
        self.sensor_id = sensor_id
        self.zone_id = zone_id
        self.sensor_type = sensor_type
        self.unit = unit
        self.failure_mode = SensorFailureMode()
    
    @abstractmethod
    def read(self, true_physical_value: float) -> tuple[float, SensorQuality]:
        """
        Reads the sensor value, applying any failure modes if configured.
        Returns the (observed_value, quality).
        """


class ActuatorCapability(BaseModel):
    min_value: float = 0.0
    max_value: float = 1.0


class Actuator(ABC):
    def __init__(self, actuator_id: str, zone_id: str, actuator_type: str, capabilities: ActuatorCapability):
        self.actuator_id = actuator_id
        self.zone_id = zone_id
        self.actuator_type = actuator_type
        self.capabilities = capabilities
        self.state: float = 0.0

    @abstractmethod
    def execute(self, target_value: float) -> bool:
        """
        Attempts to execute a command.
        Returns True if successful, False if rejected (e.g. out of range or hardware fault).
        """
        if target_value < self.capabilities.min_value or target_value > self.capabilities.max_value:
            return False
        self.state = target_value
        return True
