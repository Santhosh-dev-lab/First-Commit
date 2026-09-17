"""
domains/polyhouse/controllers/baseline.py

Crop-agnostic Baseline Controller.

Produces control actions by comparing current environment against
crop-derived targets. Does NOT hardcode any crop-specific threshold
(no "tomato_temperature_min", no "lettuce_humidity_max").

All targets are read from:

    CropProfile.constraints  →  ZoneControlContext.target_*

Decision logic
--------------
A set of independent if-threshold rules per actuator type.

  if temp > target + band:
      VENT = open; FAN = on
  elif temp < target - band:
      HEATER = on; VENT = closed

  if moisture < target - band:
      PUMP = on
  elif moisture > target + band:
      PUMP = off

  etc.

This is the first baseline policy. It is intentionally simple and
deterministic. The optimizer can later evaluate alternative policies
without changing the controller interface.
"""

from __future__ import annotations

from domains.polyhouse.controllers.base import (
    ActionType,
    ActuatorType,
    ControlAction,
    Controller,
    ControlPlan,
    ControlPolicy,
    ZoneControlContext,
)

# ---------------------------------------------------------------------------
# Baseline control policy (crop-agnostic)
# ---------------------------------------------------------------------------


class BaselineControlPolicy(ControlPolicy):
    """
    Rule-based control policy.

    Targets are provided through ZoneControlContext (derived from
    CropProfile.constraints), not hardcoded here.
    """

    _VERSION   = "1.1.0"

    def __init__(
        self,
        policy_id: str = "baseline-rule-based",
        temp_band_c: float = 2.0,
        humid_band_pct: float = 5.0,
        moisture_band: float = 5.0,
        co2_band_ppm: float = 100.0,
    ) -> None:
        self._policy_id = policy_id
        self._TEMP_BAND_C = temp_band_c
        self._HUMID_BAND_PCT = humid_band_pct
        self._MOISTURE_BAND = moisture_band
        self._CO2_BAND_PPM = co2_band_ppm

    @property
    def policy_id(self) -> str:
        return self._policy_id

    @property
    def version(self) -> str:
        return self._VERSION

    def decide(self, context: ZoneControlContext) -> list[ControlAction]:
        actions: list[ControlAction] = []
        z = context.zone_id
        t = context.temperature_c
        tt = context.target_temperature_c
        m = context.substrate_moisture_percent
        tm = context.target_moisture_percent
        h = context.humidity_percent
        th = context.target_humidity_percent

        # --- Temperature control ---
        if t > tt + self._TEMP_BAND_C:
            actions.append(ControlAction(
                zone_id=z, actuator_type=ActuatorType.VENT, actuator_id=f"vent-{z}",
                action_type=ActionType.SET_VALUE, target_value=min(1.0, (t - tt) / 10.0),
                duration_s=3600.0,
                reason=f"Temp {t:.1f}°C > target {tt:.1f}°C — open vent",
                policy_version=self._VERSION,
            ))
            if t > tt + 4.0:
                actions.append(ControlAction(
                    zone_id=z, actuator_type=ActuatorType.FAN, actuator_id=f"fan-{z}",
                    action_type=ActionType.SET_ON, target_value=1.0,
                    duration_s=3600.0,
                    reason=f"Temp {t:.1f}°C > target+4 — activate fan",
                    policy_version=self._VERSION,
                ))
        elif t < tt - self._TEMP_BAND_C:
            actions.append(ControlAction(
                zone_id=z, actuator_type=ActuatorType.HEATER, actuator_id=f"heater-{z}",
                action_type=ActionType.SET_ON, target_value=1.0,
                duration_s=3600.0,
                reason=f"Temp {t:.1f}°C < target {tt:.1f}°C — activate heater",
                policy_version=self._VERSION,
            ))
            actions.append(ControlAction(
                zone_id=z, actuator_type=ActuatorType.VENT, actuator_id=f"vent-{z}",
                action_type=ActionType.SET_VALUE, target_value=0.0,
                duration_s=3600.0,
                reason="Close vent to retain heat",
                policy_version=self._VERSION,
            ))
        else:
            # Within band — heater off, vent minimal
            actions.append(ControlAction(
                zone_id=z, actuator_type=ActuatorType.HEATER, actuator_id=f"heater-{z}",
                action_type=ActionType.SET_OFF, target_value=0.0,
                duration_s=3600.0,
                reason="Temperature within target band",
                policy_version=self._VERSION,
            ))

        # --- Humidity control ---
        if h < th - self._HUMID_BAND_PCT:
            actions.append(ControlAction(
                zone_id=z, actuator_type=ActuatorType.FOGGER, actuator_id=f"fogger-{z}",
                action_type=ActionType.SET_ON, target_value=1.0,
                duration_s=1800.0,
                reason=f"Humidity {h:.1f}% < target {th:.1f}% — activate fogger",
                policy_version=self._VERSION,
            ))

        # --- Moisture / irrigation ---
        if m < tm - self._MOISTURE_BAND and context.water_available_l > 10.0:
            actions.append(ControlAction(
                zone_id=z, actuator_type=ActuatorType.PUMP, actuator_id=f"pump-{z}",
                action_type=ActionType.SET_ON, target_value=1.0,
                duration_s=1800.0,
                reason=f"Moisture {m:.1f}% < target {tm:.1f}% — activate pump",
                policy_version=self._VERSION,
            ))
        elif m > tm + self._MOISTURE_BAND:
            actions.append(ControlAction(
                zone_id=z, actuator_type=ActuatorType.PUMP, actuator_id=f"pump-{z}",
                action_type=ActionType.SET_OFF, target_value=0.0,
                duration_s=3600.0,
                reason=f"Moisture {m:.1f}% > target — stop pump",
                policy_version=self._VERSION,
            ))

        return actions


# ---------------------------------------------------------------------------
# Baseline Controller
# ---------------------------------------------------------------------------


class BaselineController(Controller):
    """
    Crop-agnostic controller that applies BaselineControlPolicy per zone.

    Accepts a dict of policy_id → ControlPolicy for extensibility.
    """

    _VERSION = "baseline-controller-1.0.0"

    def __init__(self, policy: ControlPolicy | None = None) -> None:
        self._policy = policy or BaselineControlPolicy()

    @property
    def version(self) -> str:
        return self._VERSION

    def plan(
        self,
        simulation_id: str,
        timestep: int,
        time_days: float,
        zone_contexts: list[ZoneControlContext],
    ) -> ControlPlan:
        """Produce a ControlPlan by applying the policy to each zone."""
        plan_id = f"plan-{simulation_id}-{timestep:05d}"
        all_actions: list[ControlAction] = []
        for ctx in zone_contexts:
            zone_actions = self._policy.decide(ctx)
            all_actions.extend(zone_actions)

        return ControlPlan(
            plan_id=plan_id,
            simulation_id=simulation_id,
            timestep=timestep,
            time_days=time_days,
            actions=all_actions,
            metadata={"policy": self._policy.policy_id, "policy_version": self._policy.version},
        )
