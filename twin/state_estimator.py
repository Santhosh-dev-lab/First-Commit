from typing import Dict
from .core import SensorReading, SensorQuality, TwinCurrentState

class StateEstimator:
    def estimate(self, raw_telemetry: Dict[str, SensorReading], current_time: str) -> TwinCurrentState:
        # Simplistic estimator mapping raw telemetry to state
        # In a real system, would handle filtering and anomaly detection
        env_state = {}
        for key in ["temperature", "humidity", "co2", "par"]:
            if key in raw_telemetry and raw_telemetry[key].quality in [SensorQuality.GOOD, SensorQuality.DEGRADED]:
                env_state[key] = raw_telemetry[key].value
            else:
                # Handle missing/invalid/stale
                # E.g. fallback to previous state or theoretical bounds
                env_state[key] = 25.0  # mock fallback
        
        moisture = 50.0
        if "moisture" in raw_telemetry and raw_telemetry["moisture"].quality == SensorQuality.GOOD:
            moisture = raw_telemetry["moisture"].value
            
        return TwinCurrentState(
            timestamp=current_time,
            environment=env_state,
            crop_biomass_kg=0.0,  # Crop state usually estimated from model + sparse measurements (vision)
            substrate_moisture=moisture
        )
