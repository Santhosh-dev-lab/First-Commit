from typing import Any
from twin.core import SensorQuality
from .models import VirtualSensorConfig
from .failures import FailureInjector

class VirtualSensor:
    """
    Virtual sensor observing the authoritative SimulationEngine state.
    """
    def __init__(self, config: VirtualSensorConfig):
        self.config = config
        self.last_value: float = 0.0

    def read(self, physical_value: float) -> tuple[float, SensorQuality]:
        val, qual_str = FailureInjector.apply_sensor_noise(physical_value, self.config, 0)
        
        if qual_str == "MISSING":
            return 0.0, SensorQuality.MISSING
        if qual_str == "STALE":
            return self.last_value, SensorQuality.STALE
            
        self.last_value = val
        
        qual = SensorQuality.GOOD
        if self.config.noise_mode in ("BIAS", "GAUSSIAN", "DRIFT") or self.config.failure_mode in ("BIASED", "DRIFTING"):
            qual = SensorQuality.DEGRADED
            
        return val, qual
