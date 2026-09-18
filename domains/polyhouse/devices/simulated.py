import random

from twin.core import SensorQuality

from .base import Actuator, ActuatorCapability, Sensor


class SimulatedSensor(Sensor):
    def read(self, true_physical_value: float) -> tuple[float, SensorQuality]:
        mode = self.failure_mode.mode
        
        if mode == "MISSING":
            return (0.0, SensorQuality.MISSING)
            
        if mode == "INVALID":
            return (-9999.0, SensorQuality.INVALID)
            
        val = true_physical_value
        
        if mode == "BIAS":
            val += self.failure_mode.bias_value
            
        if mode == "NOISE":
            val += random.gauss(0.0, self.failure_mode.noise_std)
            
        quality = SensorQuality.GOOD
        if mode in ("BIAS", "NOISE"):
            quality = SensorQuality.DEGRADED
            
        return (val, quality)


class SimulatedPump(Actuator):
    def __init__(self, actuator_id: str, zone_id: str):
        # A pump that can deliver up to 10000 L/day
        super().__init__(actuator_id, zone_id, "pump", ActuatorCapability(min_value=0.0, max_value=1.0))
        self.flow_capacity_l_day = 10000.0
        
    def current_flow(self) -> float:
        return self.state * self.flow_capacity_l_day
        
    def execute(self, target_value: float) -> bool:
        return super().execute(target_value)


class SimulatedVent(Actuator):
    def __init__(self, actuator_id: str, zone_id: str):
        super().__init__(actuator_id, zone_id, "vent", ActuatorCapability(min_value=0.0, max_value=1.0))
        
    def execute(self, target_value: float) -> bool:
        return super().execute(target_value)
