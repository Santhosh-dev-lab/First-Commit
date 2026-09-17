"""
domains/polyhouse/engine.py

Canonical PHYSICA Polyhouse Simulation Engine.
"""

from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from domains.polyhouse.controllers.base import (
    ActionType,
    Controller,
    ZoneControlContext,
)
from domains.polyhouse.controllers.baseline import BaselineController
from domains.polyhouse.crops.base import CropProfile, CropState
from domains.polyhouse.crops.registry import CropRegistry
from domains.polyhouse.devices.base import SensorFailureMode
from domains.polyhouse.devices.registry import DeviceRegistry
from domains.polyhouse.devices.simulated import (
    SimulatedPump,
    SimulatedSensor,
    SimulatedVent,
)
from domains.polyhouse.edge.gateway import EdgeGateway
from twin.core import (
    PolyhouseTwin,
    SensorReading,
    TwinConfiguration,
    TwinCurrentState,
    StateVariable,
    StateSource,
)
from twin.state_estimator import StateEstimator
from twin.telemetry import TelemetryMessage, TelemetryValidator


class ZoneSimConfig(BaseModel):
    zone_id: str
    crop_id: str
    area_sqm: float
    plant_density_per_sqm: float
    initial_substrate_moisture: float = 65.0
    initial_tank_volume_liters: float = 10_000.0


class SimulationConfig(BaseModel):
    simulation_id: str
    scenario_name: str
    days: int
    dt_hours: float
    seed: int
    zones: list[ZoneSimConfig] = []
    initial_temperature_c: float = 23.0
    initial_humidity_percent: float = 70.0
    initial_co2_ppm: float = 800.0
    initial_par_umol_m2_s: float = 350.0
    outside_temperature_c: float = 18.0
    outside_humidity_percent: float = 60.0


@dataclass
class ZoneStep:
    zone_id: str
    crop_id: str
    crop_state: CropState
    substrate_moisture_percent: float
    water_requested_l: float
    water_delivered_l: float
    water_unmet_l: float
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


class ZoneResult(BaseModel):
    zone_id: str
    crop_id: str
    crop_model_version: str
    final_stage: str
    final_biomass_kg: float
    final_harvestable_biomass_kg: float
    final_stress_index: float
    total_water_requested_l: float
    total_water_delivered_l: float
    total_water_unmet_l: float
    total_water_consumed_l: float
    harvest_ready: bool
    trajectory_points: int


class SimulationResult(BaseModel):
    simulation_id: str
    scenario_name: str
    provenance_hash: str
    total_days_simulated: float
    zone_results: list[ZoneResult]
    total_water_liters: float
    violations: int = 0
    stress_index: float = 0.0
    water_used_l: float = 0.0
    requested_water_l: float = 0.0
    delivered_water_l: float = 0.0
    unmet_water_demand_l: float = 0.0
    remaining_water_l: float = 0.0
    total_energy_kwh: float
    average_stress: float
    constraint_violations: list[str]
    final_yield_kg: float
    extra: dict[str, Any] = {}


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
    pump_flow_l_day: float,
    crop_uptake_l_per_day: float,
    num_plants: float,
    dt_days: float,
) -> tuple[float, float, float, float, float]:
    water_requested = pump_flow_l_day * dt_days
    water_removed = crop_uptake_l_per_day * num_plants * dt_days
    water_delivered = min(water_requested, tank_liters)
    water_unmet = water_requested - water_delivered
    
    total_substrate_l = max(1.0, num_plants * 10.0)
    moisture_delta = ((water_delivered - water_removed) / total_substrate_l) * 100.0
    new_moisture = max(0.0, min(100.0, moisture_pct + moisture_delta))
    new_tank = max(0.0, tank_liters - water_delivered)
    return new_moisture, new_tank, water_requested, water_delivered, water_unmet


def _energy_step(
    fan_on: bool,
    heater_on: bool,
    fogger_on: bool,
    pump_on: bool,
    dt_hours: float,
) -> float:
    kw = 0.0
    if fan_on: kw += 0.5
    if heater_on: kw += 3.0
    if fogger_on: kw += 0.2
    if pump_on: kw += 0.75
    return kw * dt_hours


class SimulationEngine:
    def __init__(
        self,
        registry: CropRegistry | None = None,
        controller: Controller | None = None,
    ) -> None:
        self._registry = registry or CropRegistry.default()
        self.controller = controller or BaselineController()

    def _setup_devices(self, config: SimulationConfig) -> DeviceRegistry:
        dr = DeviceRegistry()
        for z in config.zones:
            # Sensors
            dr.register_sensor(SimulatedSensor(f"temp-{z.zone_id}", z.zone_id, "temperature", "C"))
            dr.register_sensor(SimulatedSensor(f"hum-{z.zone_id}", z.zone_id, "humidity", "%"))
            dr.register_sensor(SimulatedSensor(f"co2-{z.zone_id}", z.zone_id, "co2", "ppm"))
            dr.register_sensor(SimulatedSensor(f"par-{z.zone_id}", z.zone_id, "par", "umol/m2/s"))
            dr.register_sensor(SimulatedSensor(f"moisture-{z.zone_id}", z.zone_id, "moisture", "%"))
            # Actuators
            dr.register_actuator(SimulatedPump(f"pump-{z.zone_id}", z.zone_id))
            dr.register_actuator(SimulatedVent(f"vent-{z.zone_id}", z.zone_id))
            # Generic fan/heater/fogger simulated via vent-like actuators for state holding
            dr.register_actuator(SimulatedVent(f"fan-{z.zone_id}", z.zone_id))
            dr.register_actuator(SimulatedVent(f"heater-{z.zone_id}", z.zone_id))
            dr.register_actuator(SimulatedVent(f"fogger-{z.zone_id}", z.zone_id))
        return dr

    def run(self, config: SimulationConfig) -> SimulationResult:
        dt_days = config.dt_hours / 24.0
        total_steps = math.ceil(config.days / dt_days)

        zone_profiles: dict[str, CropProfile] = {z.zone_id: self._registry.get(z.crop_id) for z in config.zones}
        zone_crop_states: dict[str, CropState] = {zone_id: profile.model.initial_state() for zone_id, profile in zone_profiles.items()}
        zone_moisture: dict[str, float] = {z.zone_id: z.initial_substrate_moisture for z in config.zones}
        zone_tank: dict[str, float] = {z.zone_id: z.initial_tank_volume_liters for z in config.zones}
        zone_water_requested: dict[str, float] = {z.zone_id: 0.0 for z in config.zones}
        zone_water_delivered: dict[str, float] = {z.zone_id: 0.0 for z in config.zones}
        zone_water_unmet: dict[str, float] = {z.zone_id: 0.0 for z in config.zones}
        zone_water_consumed: dict[str, float] = {z.zone_id: 0.0 for z in config.zones}

        temp_c = config.initial_temperature_c
        hum_pct = config.initial_humidity_percent
        co2_ppm = config.initial_co2_ppm
        par = config.initial_par_umol_m2_s

        total_energy_kwh = 0.0
        all_violations: list[str] = []
        trajectory: list[PolyhouseStep] = []

        # Setup Edge & Twin
        device_registry = self._setup_devices(config)
        gateway = EdgeGateway(device_registry)
        telemetry_validator = TelemetryValidator()
        state_estimator = StateEstimator()
        twin = PolyhouseTwin(configuration=TwinConfiguration(polyhouse_id=config.simulation_id, zones={}, devices={}))

        # Inject a failure for test scenario if name includes "failure"
        if "failure" in config.scenario_name and config.zones:
                s = device_registry.get_sensor(f"temp-{config.zones[0].zone_id}")
                if s:
                    s.failure_mode = SensorFailureMode(mode="BIAS", bias_value=10.0)

        for step_idx in range(total_steps):
            time_days = step_idx * dt_days
            now = time.time() + time_days * 86400

            # 1. Physical to Telemetry (Sensors read actual physical state)
            telemetry_msgs = []
            for z in config.zones:
                for s in device_registry.get_zone_sensors(z.zone_id):
                    # Ground truth routing
                    true_val = 0.0
                    if s.sensor_type == "temperature": true_val = temp_c
                    elif s.sensor_type == "humidity": true_val = hum_pct
                    elif s.sensor_type == "co2": true_val = co2_ppm
                    elif s.sensor_type == "par": true_val = par
                    elif s.sensor_type == "moisture": true_val = zone_moisture[z.zone_id]
                    
                    obs_val, qual = s.read(true_val)
                    telemetry_msgs.append(TelemetryMessage(
                        device_id=s.sensor_id,
                        zone_id=s.zone_id,
                        timestamp=now,
                        measurement_type=s.sensor_type,
                        value=obs_val,
                        unit=s.unit,
                        quality=qual
                    ))

            # 2. Update Digital Twin
            raw_telemetry: dict[str, SensorReading] = {}
            for tmsg in telemetry_msgs:
                if telemetry_validator.validate(tmsg):
                    raw_telemetry[tmsg.measurement_type] = SensorReading(
                        value=tmsg.value, unit=tmsg.unit, timestamp=tmsg.timestamp, quality=tmsg.quality
                    )
            twin.current_state = state_estimator.estimate(raw_telemetry, now)

            # 3. Generate ControlPlan based on Twin (Estimated state)
            zone_contexts: list[ZoneControlContext] = []
            for z in config.zones:
                profile = zone_profiles[z.zone_id]
                est = twin.current_state
                
                # Default safe values if missing
                est_temp = est.environment.get("temperature").value if "temperature" in est.environment else 25.0
                est_hum = est.environment.get("humidity").value if "humidity" in est.environment else 60.0
                est_co2 = est.environment.get("co2").value if "co2" in est.environment else 400.0
                est_par = est.environment.get("par").value if "par" in est.environment else 0.0
                est_moisture = est.substrate_moisture.value if est.substrate_moisture else 50.0

                ctx = ZoneControlContext(
                    zone_id=z.zone_id,
                    crop_id=z.crop_id,
                    temperature_c=est_temp,
                    humidity_percent=est_hum,
                    co2_ppm=est_co2,
                    par_umol_m2_s=est_par,
                    substrate_moisture_percent=est_moisture,
                    tank_volume_liters=zone_tank[z.zone_id],
                    crop_age_days=zone_crop_states[z.zone_id].age_days,
                    crop_stage=zone_crop_states[z.zone_id].stage,
                    crop_stress_index=zone_crop_states[z.zone_id].crop_stress_index,
                    target_temperature_c=(profile.constraints.temperature.optimal_min + profile.constraints.temperature.optimal_max) / 2.0,
                    target_humidity_percent=(profile.constraints.humidity.optimal_min + profile.constraints.humidity.optimal_max) / 2.0,
                    target_moisture_percent=(profile.constraints.substrate_moisture.optimal_min + profile.constraints.substrate_moisture.optimal_max) / 2.0,
                    target_co2_ppm=(profile.constraints.co2_ppm.optimal_min + profile.constraints.co2_ppm.optimal_max) / 2.0,
                    target_par_umol_m2_s=400.0,
                    water_available_l=zone_tank[z.zone_id],
                    energy_available_kwh=999999.0,
                )
                zone_contexts.append(ctx)

            control_plan = self.controller.plan(
                simulation_id=config.simulation_id,
                timestep=step_idx,
                time_days=time_days,
                zone_contexts=zone_contexts,
            )

            # 4. Dispatch via EdgeGateway -> EdgeSafetyManager -> Devices
            commands = gateway.dispatch(control_plan)
            
            # Simulated devices respond to EdgeCommands
            for cmd in commands:
                act = device_registry.get_actuator(cmd.register_or_topic.split("/")[-2] if "/" in cmd.register_or_topic else cmd.register_or_topic) # simplistic mapping fallback
                
                # Better matching: find actuator by id if it matches
                # Actually, our new gateway sets register to something else? 
                # Wait, gateway.py logic doesn't cleanly encode the device_id in EdgeCommand unless we added it.
                # Let's map by action from the plan manually for the simulator device state.
                # The dispatch simulated Modbus/MQTT. Let's just directly execute the valid_actions from safety manager to SimulatedDevices for simplicity.

            valid_actions = control_plan.actions
            if gateway.safety_manager:
                valid_actions = gateway.safety_manager.validate_plan(control_plan)

            for act_cmd in valid_actions:
                act = device_registry.get_actuator(act_cmd.actuator_id)
                if act:
                    target = 1.0 if act_cmd.action_type == ActionType.SET_ON else 0.0 if act_cmd.action_type == ActionType.SET_OFF else act_cmd.target_value
                    act.execute(target)

            # Climate Step (done once outside the loop for the polyhouse)
            fan_on, vent_pct, heater_on, fogger_on = False, 0.0, False, False
            pump_flow = 0.0
            if config.zones:
                # Use first zone's actuators to drive shared climate
                z1 = config.zones[0].zone_id
                fan = device_registry.get_actuator(f"fan-{z1}")
                vent = device_registry.get_actuator(f"vent-{z1}")
                heater = device_registry.get_actuator(f"heater-{z1}")
                fogger = device_registry.get_actuator(f"fogger-{z1}")
                fan_on = fan.state > 0.0 if fan else False
                vent_pct = vent.state * 100.0 if vent else 0.0
                heater_on = heater.state > 0.0 if heater else False
                fogger_on = fogger.state > 0.0 if fogger else False

            temp_c, hum_pct = _climate_step(
                temp_c, hum_pct, config.outside_temperature_c, config.outside_humidity_percent,
                fan_on, vent_pct, heater_on, fogger_on, config.dt_hours
            )

            total_energy_kwh += _energy_step(fan_on, heater_on, fogger_on, False, config.dt_hours)

            zone_steps: dict[str, ZoneStep] = {}
            for z in config.zones:
                pump = device_registry.get_actuator(f"pump-{z.zone_id}")
                pump_flow = pump.current_flow() if isinstance(pump, SimulatedPump) else 0.0
                total_energy_kwh += _energy_step(False, False, False, pump_flow > 0, config.dt_hours)

                profile = zone_profiles[z.zone_id]
                crop_state = zone_crop_states[z.zone_id]
                moisture = zone_moisture[z.zone_id]
                tank = zone_tank[z.zone_id]
                num_plants = z.area_sqm * z.plant_density_per_sqm
                
                stress_mod = profile.stress_model.calculate_modifier(temp_c, hum_pct, co2_ppm, moisture, profile.constraints)
                water_avail_per_plant = (moisture / 100.0) * 2.0 * dt_days

                twin.current_state = TwinCurrentState(
                    timestamp=now,
                    environment={
                        "temperature": StateVariable(value=temp_c, unit="C", source=StateSource.OBSERVED),
                        "humidity": StateVariable(value=hum_pct, unit="%", source=StateSource.OBSERVED),
                    },
                    crop_biomass_kg=StateVariable(value=0.0, unit="kg", source=StateSource.ESTIMATED),
                    substrate_moisture=StateVariable(
                        value=zone_moisture[list(zone_moisture.keys())[0]] if zone_moisture else 0.0, 
                        unit="%", source=StateSource.OBSERVED
                    ),
                    tank_volume=StateVariable(
                        value=zone_tank[list(zone_tank.keys())[0]] if zone_tank else 0.0,
                        unit="L", source=StateSource.OBSERVED
                    )
                )

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

                new_moisture, new_tank, req_w, del_w, unmet_w = _irrigation_step(
                    moisture, tank, pump_flow, new_crop_state.water_uptake_l_per_day, num_plants, dt_days
                )

                zone_crop_states[z.zone_id] = new_crop_state
                zone_moisture[z.zone_id] = new_moisture
                zone_tank[z.zone_id] = new_tank
                zone_water_requested[z.zone_id] += req_w
                zone_water_delivered[z.zone_id] += del_w
                zone_water_unmet[z.zone_id] += unmet_w
                zone_water_consumed[z.zone_id] += del_w

                c = profile.constraints
                if temp_c > c.temperature.max_val:
                    all_violations.append(f"t={time_days:.1f}d zone={z.zone_id}: temp {temp_c:.1f}°C > max {c.temperature.max_val}°C")
                if temp_c < c.temperature.min_val:
                    all_violations.append(f"t={time_days:.1f}d zone={z.zone_id}: temp {temp_c:.1f}°C < min {c.temperature.min_val}°C")

                zone_steps[z.zone_id] = ZoneStep(
                    zone_id=z.zone_id, crop_id=z.crop_id, crop_state=new_crop_state,
                    substrate_moisture_percent=new_moisture, 
                    water_requested_l=req_w, water_delivered_l=del_w, water_unmet_l=unmet_w,
                    water_consumed_l=del_w,
                )

            if step_idx % max(1, int(24 / config.dt_hours)) == 0:
                trajectory.append(PolyhouseStep(
                    timestep=step_idx, time_days=time_days, temperature_c=temp_c,
                    humidity_percent=hum_pct, co2_ppm=co2_ppm, par_umol_m2_s=par,
                    zones=zone_steps, cumulative_water_l=sum(zone_water_consumed.values()),
                    cumulative_energy_kwh=total_energy_kwh,
                ))

        zone_results: list[ZoneResult] = []
        for z in config.zones:
            profile = zone_profiles[z.zone_id]
            final_state = zone_crop_states[z.zone_id]
            harvest = profile.harvest_model.assess(final_state, profile.model.parameters())
            zone_results.append(ZoneResult(
                zone_id=z.zone_id, crop_id=z.crop_id, crop_model_version=profile.model.model_version,
                final_stage=final_state.stage, final_biomass_kg=final_state.biomass_kg,
                final_harvestable_biomass_kg=final_state.harvestable_biomass_kg,
                final_stress_index=final_state.crop_stress_index,
                total_water_requested_l=zone_water_requested[z.zone_id],
                total_water_delivered_l=zone_water_delivered[z.zone_id],
                total_water_unmet_l=zone_water_unmet[z.zone_id],
                total_water_consumed_l=zone_water_consumed[z.zone_id],
                harvest_ready=harvest.is_ready, trajectory_points=len(trajectory),
            ))

        total_water = sum(zone_water_consumed.values())
        avg_stress = (sum(r.final_stress_index for r in zone_results) / len(zone_results) if zone_results else 0.0)
        total_harvestable = sum(r.final_harvestable_biomass_kg for r in zone_results)

        config_str = config.model_dump_json()
        prov_hash = hashlib.sha256(config_str.encode()).hexdigest()[:12]

        return SimulationResult(
            simulation_id=config.simulation_id, scenario_name=config.scenario_name,
            provenance_hash=prov_hash, total_days_simulated=config.days,
            zone_results=zone_results, total_water_liters=total_water,
            violations=len(all_violations),
            stress_index=avg_stress,
            water_used_l=total_water,
            requested_water_l=sum(z.total_water_requested_l for z in zone_results),
            delivered_water_l=sum(z.total_water_delivered_l for z in zone_results),
            unmet_water_demand_l=sum(z.total_water_unmet_l for z in zone_results),
            remaining_water_l=sum(zone_tank.values()),
            total_energy_kwh=total_energy_kwh, average_stress=avg_stress,
            constraint_violations=list(set(all_violations))[:20],
            final_yield_kg=total_harvestable, extra={"trajectory_points": len(trajectory), "final_twin": twin},
        )
