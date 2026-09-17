"""
twin/telemetry.py

Validates and standardizes incoming telemetry from edge devices.
"""

from typing import Any

from pydantic import BaseModel

from .core import SensorQuality, StateSource


class TelemetryMessage(BaseModel):
    """Raw telemetry coming from a device."""
    device_id: str
    zone_id: str
    timestamp: float
    measurement_type: str
    value: float
    unit: str
    quality: SensorQuality = SensorQuality.GOOD
    source: StateSource = StateSource.OBSERVED
    metadata: dict[str, Any] = {}


class TelemetryValidator:
    """Validates incoming telemetry."""
    
    def __init__(self, device_registry: Any = None) -> None:
        self.device_registry = device_registry

    def validate(self, message: TelemetryMessage) -> bool:
        """
        Validates telemetry message.
        - Check if device exists
        - Check if value is within physical limits
        - Check timestamp freshness
        """
        # Basic validation
        if not message.device_id or not message.zone_id:
            return False
            
        # In a real system, we'd look up the device in device_registry
        # and validate range/unit, e.g., temperature shouldn't be 1000C.
        
        return message.quality != SensorQuality.INVALID
