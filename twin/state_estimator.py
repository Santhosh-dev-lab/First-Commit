from .core import (
    SensorQuality,
    SensorReading,
    StateSource,
    StateVariable,
    TwinCurrentState,
)


class StateEstimator:
    def estimate(self, raw_telemetry: dict[str, SensorReading], current_time: float) -> TwinCurrentState:
        # Simplistic estimator mapping raw telemetry to state
        # In a real system, would handle filtering and anomaly detection
        env_state: dict[str, StateVariable] = {}
        for key in ["temperature", "humidity", "co2", "par"]:
            if key in raw_telemetry and raw_telemetry[key].quality in [SensorQuality.GOOD, SensorQuality.DEGRADED]:
                env_state[key] = StateVariable(
                    value=raw_telemetry[key].value,
                    unit=raw_telemetry[key].unit,
                    source=StateSource.OBSERVED
                )
            else:
                # Handle missing/invalid/stale
                # E.g. fallback to previous state or theoretical bounds
                # For now, mark as ESTIMATED
                env_state[key] = StateVariable(
                    value=25.0,  # mock fallback
                    unit="unknown",
                    source=StateSource.ESTIMATED
                )
        
        moisture = StateVariable(value=50.0, unit="%", source=StateSource.ESTIMATED)
        if "moisture" in raw_telemetry and raw_telemetry["moisture"].quality == SensorQuality.GOOD:
            moisture = StateVariable(
                value=raw_telemetry["moisture"].value,
                unit=raw_telemetry["moisture"].unit,
                source=StateSource.OBSERVED
            )
            
        return TwinCurrentState(
            timestamp=current_time,
            environment=env_state,
            crop_biomass_kg=StateVariable(value=0.0, unit="kg", source=StateSource.ESTIMATED),
            substrate_moisture=moisture
        )
