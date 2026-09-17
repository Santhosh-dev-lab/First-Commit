from enum import Enum

from compiler.ir.models import PhysicalIR
from pydantic import BaseModel


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class Diagnostic(BaseModel):
    code: str
    severity: Severity
    message: str
    location: str | None = None
    suggested_resolution: str | None = None

class ValidationResult(BaseModel):
    is_valid: bool
    diagnostics: list[Diagnostic]

class SemanticValidator:
    def validate(self, ir: PhysicalIR) -> ValidationResult:
        diagnostics = []
        is_valid = True

        # Check duplicate zone IDs
        zone_ids = set()
        for zone in ir.polyhouse.zones:
            if zone.zone_id in zone_ids:
                diagnostics.append(Diagnostic(
                    code="P101",
                    severity=Severity.ERROR,
                    message=f"Duplicate zone ID: {zone.zone_id}"
                ))
                is_valid = False
            zone_ids.add(zone.zone_id)

        # Check sensor IDs and zone existence
        sensor_ids = set()
        for sensor in ir.polyhouse.sensors:
            if sensor.sensor_id in sensor_ids:
                diagnostics.append(Diagnostic(
                    code="P102",
                    severity=Severity.ERROR,
                    message=f"Duplicate sensor ID: {sensor.sensor_id}"
                ))
                is_valid = False
            sensor_ids.add(sensor.sensor_id)
            if sensor.zone_id not in zone_ids:
                diagnostics.append(Diagnostic(
                    code="P103",
                    severity=Severity.ERROR,
                    message=f"Sensor {sensor.sensor_id} references unknown zone {sensor.zone_id}"
                ))
                is_valid = False
        
        # Infeasible objective checking stub
        if ir.objective.target > 100000:
            diagnostics.append(Diagnostic(
                code="P104",
                severity=Severity.ERROR,
                message="The requested target cannot be achieved under the specified physical constraints.",
                suggested_resolution="Reduce the yield target or increase polyhouse area."
            ))
            is_valid = False

        return ValidationResult(is_valid=is_valid, diagnostics=diagnostics)
