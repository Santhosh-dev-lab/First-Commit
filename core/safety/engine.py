"""
core/safety/engine.py

PHYSICA Safety Verification Engine.

The safety engine is CROP-INDEPENDENT. It evaluates constraints
that are either:

  1. Global (apply to all zones and crops)
  2. Crop-specific (derived from CropProfile.constraints)

Safety verification must occur BEFORE plan execution and DURING
edge runtime. If an optimizer proposes an unsafe action: REJECT IT.

This module defines:

  SafetyRule         — a named constraint check
  SafetyViolation    — a recorded violation
  SafetySeverity     — CRITICAL / WARNING / INFO
  SafetyResult       — output of one verification pass
  SafetyVerifier     — evaluates a set of rules against current state
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from domains.polyhouse.crops.registry import CropRegistry

# ---------------------------------------------------------------------------
# Severity
# ---------------------------------------------------------------------------


class SafetySeverity(str, Enum):
    CRITICAL = "CRITICAL"   # Must block execution
    WARNING  = "WARNING"    # Flagged but may proceed
    INFO     = "INFO"       # Informational


# ---------------------------------------------------------------------------
# Violation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SafetyViolation:
    rule_id: str
    severity: SafetySeverity
    zone_id: str | None
    crop_id: str | None
    message: str
    actual_value: float | None = None
    limit_value: float | None = None


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------


@dataclass
class SafetyResult:
    is_safe: bool                              # False if any CRITICAL violation
    violations: list[SafetyViolation] = field(default_factory=list)
    warnings: list[SafetyViolation]  = field(default_factory=list)

    @property
    def all_findings(self) -> list[SafetyViolation]:
        return self.violations + self.warnings


# ---------------------------------------------------------------------------
# Safety Rule (callable)
# ---------------------------------------------------------------------------

#: A SafetyCheck receives (env_state_dict, zone_id, crop_id, registry)
#: and returns a list of SafetyViolation objects (empty = pass).
SafetyCheckFn = Callable[
    [dict[str, float], str | None, str | None, CropRegistry | None],
    list[SafetyViolation],
]


@dataclass(frozen=True)
class SafetyRule:
    rule_id: str
    description: str
    severity: SafetySeverity
    check: SafetyCheckFn


# ---------------------------------------------------------------------------
# Built-in rules
# ---------------------------------------------------------------------------


def _rule_global_max_temp() -> SafetyRule:
    GLOBAL_MAX_TEMP = 45.0  # Absolute polyhouse structural safety limit

    def check(
        state: dict[str, float],
        zone_id: str | None,
        crop_id: str | None,
        registry: CropRegistry | None,
    ) -> list[SafetyViolation]:
        temp = state.get("temperature_c", 0.0)
        if temp > GLOBAL_MAX_TEMP:
            return [SafetyViolation(
                rule_id="GLOBAL_MAX_TEMP",
                severity=SafetySeverity.CRITICAL,
                zone_id=zone_id,
                crop_id=crop_id,
                message=f"Temperature {temp:.1f}°C exceeds absolute limit {GLOBAL_MAX_TEMP}°C",
                actual_value=temp,
                limit_value=GLOBAL_MAX_TEMP,
            )]
        return []

    return SafetyRule(
        rule_id="GLOBAL_MAX_TEMP",
        description="Global maximum polyhouse temperature safety limit",
        severity=SafetySeverity.CRITICAL,
        check=check,
    )


def _rule_global_min_temp() -> SafetyRule:
    GLOBAL_MIN_TEMP = 2.0  # Frost protection

    def check(
        state: dict[str, float],
        zone_id: str | None,
        crop_id: str | None,
        registry: CropRegistry | None,
    ) -> list[SafetyViolation]:
        temp = state.get("temperature_c", 20.0)
        if temp < GLOBAL_MIN_TEMP:
            return [SafetyViolation(
                rule_id="GLOBAL_MIN_TEMP",
                severity=SafetySeverity.CRITICAL,
                zone_id=zone_id,
                crop_id=crop_id,
                message=f"Temperature {temp:.1f}°C below frost-protection limit {GLOBAL_MIN_TEMP}°C",
                actual_value=temp,
                limit_value=GLOBAL_MIN_TEMP,
            )]
        return []

    return SafetyRule(
        rule_id="GLOBAL_MIN_TEMP",
        description="Global minimum polyhouse temperature (frost protection)",
        severity=SafetySeverity.CRITICAL,
        check=check,
    )


def _rule_global_max_humidity() -> SafetyRule:
    GLOBAL_MAX_HUM = 98.0  # Condensation / mould risk

    def check(
        state: dict[str, float],
        zone_id: str | None,
        crop_id: str | None,
        registry: CropRegistry | None,
    ) -> list[SafetyViolation]:
        hum = state.get("humidity_percent", 0.0)
        if hum > GLOBAL_MAX_HUM:
            return [SafetyViolation(
                rule_id="GLOBAL_MAX_HUMIDITY",
                severity=SafetySeverity.WARNING,
                zone_id=zone_id,
                crop_id=crop_id,
                message=f"Humidity {hum:.1f}% exceeds safe limit {GLOBAL_MAX_HUM}%",
                actual_value=hum,
                limit_value=GLOBAL_MAX_HUM,
            )]
        return []

    return SafetyRule(
        rule_id="GLOBAL_MAX_HUMIDITY",
        description="Global maximum humidity (condensation / mould risk)",
        severity=SafetySeverity.WARNING,
        check=check,
    )


def _rule_global_max_co2() -> SafetyRule:
    GLOBAL_MAX_CO2 = 5000.0  # OSHA safety threshold ppm

    def check(
        state: dict[str, float],
        zone_id: str | None,
        crop_id: str | None,
        registry: CropRegistry | None,
    ) -> list[SafetyViolation]:
        co2 = state.get("co2_ppm", 400.0)
        if co2 > GLOBAL_MAX_CO2:
            return [SafetyViolation(
                rule_id="GLOBAL_MAX_CO2",
                severity=SafetySeverity.CRITICAL,
                zone_id=zone_id,
                crop_id=crop_id,
                message=f"CO2 {co2:.0f} ppm exceeds occupational safety limit {GLOBAL_MAX_CO2:.0f} ppm",
                actual_value=co2,
                limit_value=GLOBAL_MAX_CO2,
            )]
        return []

    return SafetyRule(
        rule_id="GLOBAL_MAX_CO2",
        description="Global CO2 occupational safety limit",
        severity=SafetySeverity.CRITICAL,
        check=check,
    )


def _rule_crop_temp_max() -> SafetyRule:
    """Crop-specific maximum temperature from CropConstraints."""

    def check(
        state: dict[str, float],
        zone_id: str | None,
        crop_id: str | None,
        registry: CropRegistry | None,
    ) -> list[SafetyViolation]:
        if not crop_id or not registry or not registry.exists(crop_id):
            return []
        profile = registry.get(crop_id)
        temp = state.get("temperature_c", 20.0)
        max_temp = profile.constraints.temperature.max_val
        if temp > max_temp:
            return [SafetyViolation(
                rule_id="CROP_MAX_TEMP",
                severity=SafetySeverity.WARNING,
                zone_id=zone_id,
                crop_id=crop_id,
                message=(
                    f"Temperature {temp:.1f}°C exceeds {profile.common_name} "
                    f"maximum {max_temp}°C"
                ),
                actual_value=temp,
                limit_value=max_temp,
            )]
        return []

    return SafetyRule(
        rule_id="CROP_MAX_TEMP",
        description="Crop-specific maximum temperature constraint",
        severity=SafetySeverity.WARNING,
        check=check,
    )


def _rule_crop_min_temp() -> SafetyRule:
    """Crop-specific minimum temperature from CropConstraints."""

    def check(
        state: dict[str, float],
        zone_id: str | None,
        crop_id: str | None,
        registry: CropRegistry | None,
    ) -> list[SafetyViolation]:
        if not crop_id or not registry or not registry.exists(crop_id):
            return []
        profile = registry.get(crop_id)
        temp = state.get("temperature_c", 20.0)
        min_temp = profile.constraints.temperature.min_val
        if temp < min_temp:
            return [SafetyViolation(
                rule_id="CROP_MIN_TEMP",
                severity=SafetySeverity.WARNING,
                zone_id=zone_id,
                crop_id=crop_id,
                message=(
                    f"Temperature {temp:.1f}°C below {profile.common_name} "
                    f"minimum {min_temp}°C"
                ),
                actual_value=temp,
                limit_value=min_temp,
            )]
        return []

    return SafetyRule(
        rule_id="CROP_MIN_TEMP",
        description="Crop-specific minimum temperature constraint",
        severity=SafetySeverity.WARNING,
        check=check,
    )


def _rule_water_availability() -> SafetyRule:
    """Warn when water tank is nearly empty."""

    def check(
        state: dict[str, float],
        zone_id: str | None,
        crop_id: str | None,
        registry: CropRegistry | None,
    ) -> list[SafetyViolation]:
        tank = state.get("tank_volume_liters", 1000.0)
        if tank < 100.0:
            return [SafetyViolation(
                rule_id="LOW_WATER",
                severity=SafetySeverity.WARNING,
                zone_id=zone_id,
                crop_id=crop_id,
                message=f"Water tank critically low: {tank:.0f} L remaining",
                actual_value=tank,
                limit_value=100.0,
            )]
        return []

    return SafetyRule(
        rule_id="LOW_WATER",
        description="Water availability warning threshold",
        severity=SafetySeverity.WARNING,
        check=check,
    )


# ---------------------------------------------------------------------------
# SafetyVerifier
# ---------------------------------------------------------------------------


class SafetyVerifier:
    """
    Evaluates a set of SafetyRules against environmental/resource state.

    The verifier is CROP-INDEPENDENT at its core.
    Crop-specific rules are enabled by passing crop_id + registry.

    Usage
    -----
    verifier = SafetyVerifier.default(registry)
    result = verifier.verify(
        state={"temperature_c": 42.0, "humidity_percent": 75.0},
        zone_id="z1",
        crop_id="lettuce",
    )
    if not result.is_safe:
        # Block execution
    """

    def __init__(self, rules: list[SafetyRule], registry: CropRegistry | None = None) -> None:
        self._rules = rules
        self._registry = registry

    @classmethod
    def default(cls, registry: CropRegistry | None = None) -> SafetyVerifier:
        """Create a SafetyVerifier with all built-in rules."""
        rules = [
            _rule_global_max_temp(),
            _rule_global_min_temp(),
            _rule_global_max_humidity(),
            _rule_global_max_co2(),
            _rule_crop_temp_max(),
            _rule_crop_min_temp(),
            _rule_water_availability(),
        ]
        return cls(rules, registry)

    def add_rule(self, rule: SafetyRule) -> None:
        """Add a custom rule."""
        self._rules.append(rule)

    def verify(
        self,
        state: dict[str, float],
        zone_id: str | None = None,
        crop_id: str | None = None,
    ) -> SafetyResult:
        """
        Evaluate all rules against the provided state dict.

        Parameters
        ----------
        state:   Dict of measured/estimated values.
                 Keys: temperature_c, humidity_percent, co2_ppm,
                       substrate_moisture_percent, tank_volume_liters, etc.
        zone_id: Optional zone identifier for context.
        crop_id: Optional crop identifier; enables crop-specific rules.
        """
        critical_violations: list[SafetyViolation] = []
        warnings: list[SafetyViolation] = []

        for rule in self._rules:
            findings = rule.check(state, zone_id, crop_id, self._registry)
            for v in findings:
                if v.severity == SafetySeverity.CRITICAL:
                    critical_violations.append(v)
                else:
                    warnings.append(v)

        return SafetyResult(
            is_safe=len(critical_violations) == 0,
            violations=critical_violations,
            warnings=warnings,
        )
