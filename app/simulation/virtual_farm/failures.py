import random

from .models import VirtualSensorConfig


class FailureInjector:
    """
    Handles stochastic/deterministic failure injection based on configuration.
    """
    
    @staticmethod
    def apply_sensor_noise(value: float, config: VirtualSensorConfig, seed: int) -> tuple[float, str]:
        # Using a deterministic random based on seed + timestamp could be done, 
        # but for simplicity we rely on the runtime's RNG.
        if config.failure_mode == "OFFLINE":
            return 0.0, "MISSING"
        if config.failure_mode == "STALE":
            # Runtime should cache the last value, we return a flag
            return value, "STALE"
            
        noise = 0.0
        if config.noise_mode == "GAUSSIAN":
            noise = random.gauss(0.0, config.noise_std)
        elif config.noise_mode == "BIAS" or config.failure_mode == "BIASED":
            noise = config.bias_value
        elif config.noise_mode == "DRIFT" or config.failure_mode == "DRIFTING":
            # Drift increases over time, requires state tracking
            noise = config.bias_value # simplified for now
            
        return value + noise, "GOOD"
