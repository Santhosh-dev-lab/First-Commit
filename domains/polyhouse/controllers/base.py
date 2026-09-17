"""
domains/polyhouse/controllers/base.py

Generic controller contracts for PHYSICA.

No crop-specific logic here. The controller reads targets from
CropProfile.constraints — it does NOT hardcode tomato or lettuce
thresholds.

Architecture
------------
STATE (ZoneClimateState + CropState + ResourceState)
        ↓
Controller.decide(zone_context)
        ↓
list[ControlAction]
        ↓
ControlPlan
        ↓
SafetyVerifier
        ↓
SimulationEngine / EdgeGateway
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Actuator types
# ---------------------------------------------------------------------------


class ActuatorType(str, Enum):
    FAN            = "FAN"
    VENT           = "VENT"
    HEATER         = "HEATER"
    FOGGER         = "FOGGER"
    PUMP           = "PUMP"
    VALVE          = "VALVE"
    GROW_LIGHT     = "GROW_LIGHT"
    CO2_INJECTOR   = "CO2_INJECTOR"
    SHADING        = "SHADING"


class ActionType(str, Enum):
    SET_ON         = "SET_ON"
    SET_OFF        = "SET_OFF"
    SET_VALUE      = "SET_VALUE"    # e.g. fan speed, vent percentage
    SET_DUTY_CYCLE = "SET_DUTY_CYCLE"


# ---------------------------------------------------------------------------
# Control action
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ControlAction:
    """
    A single actuator command produced by a controller.

    Contains all metadata needed for safety verification and audit.
    """
    zone_id: str
    actuator_type: ActuatorType
    actuator_id: str
    action_type: ActionType
    target_value: float          # 0.0 = off/min; 1.0 = on/max; or physical unit
    duration_s: float            # seconds this action should remain active
    reason: str                  # human-readable justification
    policy_version: str
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Control plan
# ---------------------------------------------------------------------------


@dataclass
class ControlPlan:
    """
    Ordered sequence of ControlActions for one control cycle.

    Produced by a Controller, verified by SafetyVerifier,
    then executed by EdgeGateway or SimulationEngine.
    """
    plan_id: str
    simulation_id: str
    timestep: int
    time_days: float
    actions: list[ControlAction] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def for_zone(self, zone_id: str) -> list[ControlAction]:
        return [a for a in self.actions if a.zone_id == zone_id]

    def of_type(self, actuator_type: ActuatorType) -> list[ControlAction]:
        return [a for a in self.actions if a.actuator_type == actuator_type]


# ---------------------------------------------------------------------------
# Zone context — what the controller sees
# ---------------------------------------------------------------------------


@dataclass
class ZoneControlContext:
    """
    All inputs a controller needs to decide on actions for one zone.

    Crop targets are obtained from CropProfile — not hardcoded.
    """
    zone_id: str
    crop_id: str
    # Environmental state
    temperature_c: float
    humidity_percent: float
    co2_ppm: float
    par_umol_m2_s: float
    # Root zone state
    substrate_moisture_percent: float
    tank_volume_liters: float
    # Crop state
    crop_age_days: float
    crop_stage: str
    crop_stress_index: float
    # Targets (derived from CropProfile.constraints — never hardcoded here)
    target_temperature_c: float
    target_humidity_percent: float
    target_moisture_percent: float
    target_co2_ppm: float
    target_par_umol_m2_s: float
    # Resource availability
    water_available_l: float
    energy_available_kwh: float


# ---------------------------------------------------------------------------
# Control policy
# ---------------------------------------------------------------------------


class ControlPolicy(ABC):
    """Abstract control policy. Decides which actuators to activate."""

    @property
    @abstractmethod
    def policy_id(self) -> str:
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        ...

    @abstractmethod
    def decide(self, context: ZoneControlContext) -> list[ControlAction]:
        """Return a list of ControlActions for this zone."""
        ...


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------


class Controller(ABC):
    """
    High-level controller that produces a full ControlPlan for all zones.

    The controller uses CropProfile.constraints to determine targets —
    it never imports individual crop implementations.
    """

    @abstractmethod
    def plan(
        self,
        simulation_id: str,
        timestep: int,
        time_days: float,
        zone_contexts: list[ZoneControlContext],
    ) -> ControlPlan:
        """Produce a ControlPlan for all zones."""
        ...
