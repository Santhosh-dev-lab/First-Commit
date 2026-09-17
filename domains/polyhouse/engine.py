"""
domains/polyhouse/engine.py

Canonical PHYSICA Polyhouse Simulation Engine.

This is ONE engine — it replaces the stub in simulation/polyhouse/engine.py.
The old module is preserved as a compatibility wrapper that re-exports
SimulationConfig and SimulationResult from here.

Design invariants
-----------------
1. No crop-specific branching (no ``if crop == "tomato"``).
2. Crops are resolved through CropRegistry.get(zone.crop_id).
3. The engine calls the generic CropModel.step() interface.
4. Environmental and irrigation models remain crop-independent.
5. Safety rules are evaluated per-step.

Multi-zone support
------------------
Each ZoneConfig maps a zone to a crop via crop_id.
Zones run independently through their crop models.
Shared resources (water, energy) are tracked at polyhouse level.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from domains.polyhouse.crops.base import CropProfile, CropState
from domains.polyhouse.crops.registry import CropRegistry
from domains.polyhouse.controllers.base import Controller, ZoneControlContext, ActuatorType, ActionType
from domains.polyhouse.controllers.baseline import BaselineController

# ---------------------------------------------------------------------------
# Configuration models
# ---------------------------------------------------------------------------


class ZoneSimConfig(BaseModel):
    """Configuration for a single zone in the simulation."""
    zone_id: str
    crop_id: str
    area_sqm: float
    plant_density_per_sqm: float
    initial_substrate_moisture: float = 65.0   # %
    initial_tank_volume_liters: float = 10_000.0


class SimulationConfig(BaseModel):
    """Top-level simulation configuration."""
    simulation_id: str
    scenario_name: str
    days: int
    dt_hours: float
    seed: int
    zones: list[ZoneSimConfig] = []
    # Environmental starting conditions
    initial_temperature_c: float = 23.0
    initial_humidity_percent: float = 70.0
    initial_co2_ppm: float = 800.0
    initial_par_umol_m2_s: float = 350.0
    # Outside conditions (constant; real system would use weather data)
    outside_temperature_c: float = 18.0
    outside_humidity_percent: float = 60.0


# ---------------------------------------------------------------------------
# Per-step state
# ---------------------------------------------------------------------------


@dataclass
class ZoneStep:
    zone_id: str
    crop_id: str
    crop_state: CropState
    substrate_moisture_percent: float
    water_consumed_l: float


@dataclass
class PolyhouseStep:
    timestep: int
    time_days: float
    temperature_c: float
    humidity_percent: float
    co2_ppm: float
    par_umol_m2_s: float
    zones: dict[str, ZoneStep]
    cumulative_water_l: float
    cumulative_energy_kwh: float
    constraint_violations: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------


class ZoneResult(BaseModel):
    zone_id: str
    crop_id: str
    crop_model_version: str
    final_stage: str
    final_biomass_kg: float
    final_harvestable_biomass_kg: float
    final_stress_index: float
    total_water_consumed_l: float
    harvest_ready: bool
    trajectory_points: int


class SimulationResult(BaseModel):
    """Aggregate result returned by SimulationEngine.run()."""
    simulation_id: str
    scenario_name: str
    provenance_hash: str
    total_days_simulated: float
    zone_results: list[ZoneResult]
    total_water_liters: float
    total_energy_kwh: float
    average_stress: float
    constraint_violations: list[str]
    # Legacy scalar fields (for backward compatibility with old CLI)
    final_yield_kg: float
    extra: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Simple deterministic climate step (crop-independent)
# ---------------------------------------------------------------------------


def _climate_step(
    temp_c: float,
    humidity_pct: float,
    outside_temp: float,
    outside_hum: float,
    fan_on: bool,
    vent_pct: float,
    heater_on: bool,
    fogger_on: bool,
    dt_hours: float,
) -> tuple[float, float]:
    """Advance climate state by dt_hours. Returns (new_temp, new_hum)."""
    temp_rate = 0.0
    if heater_on:
        temp_rate += 2.0
    if vent_pct > 0:
        temp_rate += (outside_temp - temp_c) * (vent_pct / 100.0) * 0.5
    if fan_on:
        temp_rate += (outside_temp - temp_c) * 0.3
    if fogger_on:
        temp_rate -= 0.8

    new_temp = temp_c + temp_rate * dt_hours

    hum_rate = 0.0
    if fogger_on:
        hum_rate += 5.0
    if vent_pct > 0:
        hum_rate += (outside_hum - humidity_pct) * (vent_pct / 100.0) * 0.5
    new_hum = max(0.0, min(100.0, humidity_pct + hum_rate * dt_hours))

    return new_temp, new_hum


def _irrigation_step(
    moisture_pct: float,
    tank_liters: float,
    pump_on: bool,
    crop_uptake_l_per_day: float,
    num_plants: float,
    dt_days: float,
) -> tuple[float, float, float]:
    """
    Advance irrigation state.
    Returns: (new_moisture, new_tank, water_consumed_l_this_step)
    """
    flow_l_per_day = 10000.0 if pump_on else 0.0
    water_added = flow_l_per_day * dt_days
    water_removed = crop_uptake_l_per_day * num_plants * dt_days
    # Tank cannot deliver more than available
    water_added = min(water_added, tank_liters)
    # Assume 10L of substrate per plant
    total_substrate_l = max(1.0, num_plants * 10.0)
    moisture_delta = ((water_added - water_removed) / total_substrate_l) * 100.0
    new_moisture = max(0.0, min(100.0, moisture_pct + moisture_delta))
    new_tank = max(0.0, tank_liters - water_added)
    return new_moisture, new_tank, water_added


def _energy_step(
    fan_on: bool,
    heater_on: bool,
    fogger_on: bool,
    pump_on: bool,
    dt_hours: float,
) -> float:
    """Estimate energy kWh for this timestep (very simplified, ASSUMED)."""
    kw = 0.0
    if fan_on:
        kw += 0.5
    if heater_on:
        kw += 3.0
    if fogger_on:
        kw += 0.2
    if pump_on:
        kw += 0.75
    return kw * dt_hours


# ---------------------------------------------------------------------------
# Canonical simulation engine
# ---------------------------------------------------------------------------


class SimulationEngine:
    """
    Crop-agnostic polyhouse simulation engine.

    The engine resolves crops through CropRegistry and calls
    CropModel.step() — it contains NO crop-specific logic.

    Parameters
    ----------
    registry: CropRegistry instance. Defaults to CropRegistry.default()
              (singleton with all built-in crops).
    """

    def __init__(
        self,
        registry: CropRegistry | None = None,
        controller: Controller | None = None,
    ) -> None:
        self._registry = registry or CropRegistry.default()
        self.controller = controller or BaselineController()

    def run(self, config: SimulationConfig) -> SimulationResult:
        """
        Execute the simulation.

        For each timestep dt_hours:
          1. Determine actuator actions (baseline control, per zone)
          2. Advance climate
          3. For each zone: advance crop model + irrigation
          4. Accumulate resources and constraint violations

        Returns SimulationResult with per-zone results and aggregate metrics.
        """
        dt_days = config.dt_hours / 24.0
        total_steps = math.ceil(config.days / dt_days)

        # Resolve crop profiles once
        zone_profiles: dict[str, CropProfile] = {}
        for z in config.zones:
            zone_profiles[z.zone_id] = self._registry.get(z.crop_id)

        # Initialise per-zone crop state
        zone_crop_states: dict[str, CropState] = {
            z.zone_id: zone_profiles[z.zone_id].model.initial_state()
            for z in config.zones
        }

        # Initialise per-zone irrigation state
        zone_moisture: dict[str, float] = {
            z.zone_id: z.initial_substrate_moisture for z in config.zones
        }
        zone_tank: dict[str, float] = {
            z.zone_id: z.initial_tank_volume_liters for z in config.zones
        }
        zone_water_consumed: dict[str, float] = {z.zone_id: 0.0 for z in config.zones}

        # Shared environment (same polyhouse, single zone climate for now)
        temp_c = config.initial_temperature_c
        hum_pct = config.initial_humidity_percent
        co2_ppm = config.initial_co2_ppm
        par = config.initial_par_umol_m2_s

        total_energy_kwh = 0.0
        all_violations: list[str] = []
        trajectory: list[PolyhouseStep] = []

        for step_idx in range(total_steps):
            time_days = step_idx * dt_days

            # Build ZoneControlContext for each zone
            zone_contexts: list[ZoneControlContext] = []
            for z in config.zones:
                profile = zone_profiles[z.zone_id]
                c_age = zone_crop_states[z.zone_id].age_days
                c_stage = zone_crop_states[z.zone_id].stage
                c_stress = zone_crop_states[z.zone_id].crop_stress_index
                
                target_temp = (
                    profile.constraints.temperature.optimal_min
                    + profile.constraints.temperature.optimal_max
                ) / 2.0
                target_moisture = (
                    profile.constraints.substrate_moisture.optimal_min
                    + profile.constraints.substrate_moisture.optimal_max
                ) / 2.0
                target_humidity = (
                    profile.constraints.humidity.optimal_min
                    + profile.constraints.humidity.optimal_max
                ) / 2.0
                target_co2 = (
                    profile.constraints.co2_ppm.optimal_min
                    + profile.constraints.co2_ppm.optimal_max
                ) / 2.0
                
                ctx = ZoneControlContext(
                    zone_id=z.zone_id,
                    crop_id=z.crop_id,
                    temperature_c=temp_c,
                    humidity_percent=hum_pct,
                    co2_ppm=co2_ppm,
                    par_umol_m2_s=par,
                    substrate_moisture_percent=zone_moisture[z.zone_id],
                    tank_volume_liters=zone_tank[z.zone_id],
                    crop_age_days=c_age,
                    crop_stage=c_stage,
                    crop_stress_index=c_stress,
                    target_temperature_c=target_temp,
                    target_humidity_percent=target_humidity,
                    target_moisture_percent=target_moisture,
                    target_co2_ppm=target_co2,
                    target_par_umol_m2_s=400.0, # Assumed for now
                    water_available_l=zone_tank[z.zone_id],
                    energy_available_kwh=999999.0, # Infinite for now
                )
                zone_contexts.append(ctx)

            # Get ControlPlan
            control_plan = self.controller.plan(
                simulation_id=config.simulation_id,
                timestep=step_idx,
                time_days=time_days,
                zone_contexts=zone_contexts,
            )

            # Apply actions to simulation inputs
            zone_actuators: dict[str, tuple[bool, float, bool, bool, bool]] = {}
            for z in config.zones:
                zone_actions = control_plan.for_zone(z.zone_id)
                fan_on = False
                vent_pct = 0.0
                heater_on = False
                fogger_on = False
                pump_on = False
                
                for a in zone_actions:
                    if a.actuator_type == ActuatorType.FAN and a.action_type == ActionType.SET_ON:
                        fan_on = True
                    if a.actuator_type == ActuatorType.HEATER and a.action_type == ActionType.SET_ON:
                        heater_on = True
                    if a.actuator_type == ActuatorType.FOGGER and a.action_type == ActionType.SET_ON:
                        fogger_on = True
                    if a.actuator_type == ActuatorType.PUMP and a.action_type == ActionType.SET_ON:
                        pump_on = True
                    if a.actuator_type == ActuatorType.PUMP and a.action_type == ActionType.SET_OFF:
                        pump_on = False
                    if a.actuator_type == ActuatorType.VENT and a.action_type == ActionType.SET_VALUE:
                        vent_pct = a.target_value * 100.0
                
                zone_actuators[z.zone_id] = (fan_on, vent_pct, heater_on, fogger_on, pump_on)

            # Use first zone's actuators for shared climate (simplification)
            if config.zones:
                fan_on, vent_pct, heater_on, fogger_on, _ = zone_actuators[
                    config.zones[0].zone_id
                ]
            else:
                fan_on, vent_pct, heater_on, fogger_on = False, 0.0, False, False

            # Advance climate
            temp_c, hum_pct = _climate_step(
                temp_c, hum_pct,
                config.outside_temperature_c, config.outside_humidity_percent,
                fan_on, vent_pct, heater_on, fogger_on,
                config.dt_hours,
            )

            # Energy this step
            step_energy = 0.0

            # Advance each zone
            zone_steps: dict[str, ZoneStep] = {}
            for z in config.zones:
                profile = zone_profiles[z.zone_id]
                crop_state = zone_crop_states[z.zone_id]
                moisture = zone_moisture[z.zone_id]
                tank = zone_tank[z.zone_id]
                _, _, _, _, pump_on = zone_actuators[z.zone_id]

                num_plants = z.area_sqm * z.plant_density_per_sqm

                # Stress modifier (crop-specific model, generic call)
                stress_mod = profile.stress_model.calculate_modifier(
                    temp_c, hum_pct, co2_ppm, moisture, profile.constraints,
                )

                # Plant draws water from substrate, not directly from the pump.
                # Assume a max of 2.0 L per plant per day available if substrate is 100% saturated.
                water_avail_per_plant = (moisture / 100.0) * 2.0 * dt_days

                # Advance crop (generic interface — no crop-specific branching)
                new_crop_state = profile.model.step(
                    current=crop_state,
                    temperature_c=temp_c,
                    humidity_percent=hum_pct,
                    co2_ppm=co2_ppm,
                    par_umol_m2_s=par,
                    substrate_moisture_percent=moisture,
                    water_available_l=water_avail_per_plant,
                    stress_modifier=stress_mod,
                    dt_days=dt_days,
                )

                # Advance irrigation
                new_moisture, new_tank, water_consumed = _irrigation_step(
                    moisture, tank, pump_on,
                    new_crop_state.water_uptake_l_per_day,
                    num_plants, dt_days,
                )

                zone_crop_states[z.zone_id] = new_crop_state
                zone_moisture[z.zone_id] = new_moisture
                zone_tank[z.zone_id] = new_tank
                zone_water_consumed[z.zone_id] += water_consumed

                # Energy for this zone's pump
                step_energy += _energy_step(
                    fan_on, heater_on, fogger_on, pump_on, config.dt_hours
                )

                # Constraint violation checks
                c = profile.constraints
                if temp_c > c.temperature.max_val:
                    all_violations.append(
                        f"t={time_days:.1f}d zone={z.zone_id}: "
                        f"temp {temp_c:.1f}°C > max {c.temperature.max_val}°C"
                    )
                if temp_c < c.temperature.min_val:
                    all_violations.append(
                        f"t={time_days:.1f}d zone={z.zone_id}: "
                        f"temp {temp_c:.1f}°C < min {c.temperature.min_val}°C"
                    )

                zone_steps[z.zone_id] = ZoneStep(
                    zone_id=z.zone_id,
                    crop_id=z.crop_id,
                    crop_state=new_crop_state,
                    substrate_moisture_percent=new_moisture,
                    water_consumed_l=water_consumed,
                )

            total_energy_kwh += step_energy

            # Record trajectory (every 24h for memory efficiency)
            if step_idx % max(1, int(24 / config.dt_hours)) == 0:
                trajectory.append(
                    PolyhouseStep(
                        timestep=step_idx,
                        time_days=time_days,
                        temperature_c=temp_c,
                        humidity_percent=hum_pct,
                        co2_ppm=co2_ppm,
                        par_umol_m2_s=par,
                        zones=zone_steps,
                        cumulative_water_l=sum(zone_water_consumed.values()),
                        cumulative_energy_kwh=total_energy_kwh,
                    )
                )

        # Build per-zone results
        zone_results: list[ZoneResult] = []
        for z in config.zones:
            profile = zone_profiles[z.zone_id]
            final_state = zone_crop_states[z.zone_id]
            harvest = profile.harvest_model.assess(final_state, profile.model.parameters())
            zone_results.append(ZoneResult(
                zone_id=z.zone_id,
                crop_id=z.crop_id,
                crop_model_version=profile.model.model_version,
                final_stage=final_state.stage,
                final_biomass_kg=final_state.biomass_kg,
                final_harvestable_biomass_kg=final_state.harvestable_biomass_kg,
                final_stress_index=final_state.crop_stress_index,
                total_water_consumed_l=zone_water_consumed[z.zone_id],
                harvest_ready=harvest.is_ready,
                trajectory_points=len(trajectory),
            ))

        # Aggregate metrics
        total_water = sum(zone_water_consumed.values())
        avg_stress = (
            sum(r.final_stress_index for r in zone_results) / len(zone_results)
            if zone_results else 0.0
        )
        total_harvestable = sum(r.final_harvestable_biomass_kg for r in zone_results)

        # Provenance hash: config fingerprint for reproducibility
        config_str = config.model_dump_json()
        prov_hash = hashlib.sha256(config_str.encode()).hexdigest()[:12]

        return SimulationResult(
            simulation_id=config.simulation_id,
            scenario_name=config.scenario_name,
            provenance_hash=prov_hash,
            total_days_simulated=config.days,
            zone_results=zone_results,
            total_water_liters=total_water,
            total_energy_kwh=total_energy_kwh,
            average_stress=avg_stress,
            constraint_violations=list(set(all_violations))[:20],  # cap for readability
            final_yield_kg=total_harvestable,
            extra={"trajectory_points": len(trajectory)},
        )
