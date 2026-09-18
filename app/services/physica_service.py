from __future__ import annotations

import time
import uuid
from typing import Any

from agents.base import MockAgentProvider
from app.api.schemas import (
    ActionResponse,
    ExecutionResponse,
    IntentRequest,
    IntentResponse,
    PlanResponse,
    ResourceResponse,
    SimulationRequest,
    SimulationResponse,
    TelemetryResponse,
    TwinResponse,
    WhatIfRequest,
    WhatIfResponse,
    ZoneResponse,
)
from app.services.repositories import execution_repo, plan_repo
from core.safety.engine import SafetyVerifier
from domains.polyhouse.crops.registry import CropRegistry
from domains.polyhouse.engine import SimulationConfig, SimulationEngine, ZoneSimConfig
from schemas.tools import (
    ControlPlanProposal,
    ExecutionState,
)


class PhysicaApplicationService:
    def __init__(self) -> None:
        self.crop_registry = CropRegistry.default()
        self.simulation_engine = SimulationEngine(registry=self.crop_registry)
        self.safety_verifier = SafetyVerifier(rules=[])
        self.agent_provider = MockAgentProvider()
        
        # Hardcoded static configuration for demo twin state
        self._demo_twin_zones = [
            ZoneSimConfig(zone_id="zone_1", crop_id="dwarf_tomato", area_sqm=500.0, plant_density_per_sqm=10.0, initial_substrate_moisture=65.0, initial_tank_volume_liters=5000.0),
            ZoneSimConfig(zone_id="zone_2", crop_id="lettuce", area_sqm=300.0, plant_density_per_sqm=15.0, initial_substrate_moisture=70.0, initial_tank_volume_liters=2000.0)
        ]
        
    def _map_simulation_result(self, res: Any) -> SimulationResponse:
        return SimulationResponse(
            simulation_id=res.simulation_id,
            scenario_name=res.scenario_name,
            provenance_hash=res.provenance_hash,
            total_days_simulated=res.total_days_simulated,
            total_water_used_l=res.water_used_l,
            violations=res.violations,
            stress_index=res.stress_index,
            requested_water_l=res.requested_water_l,
            delivered_water_l=res.delivered_water_l,
            unmet_water_demand_l=res.unmet_water_demand_l,
            remaining_water_l=res.remaining_water_l,
            final_yield_kg=res.final_yield_kg
        )

    def get_twin_state(self) -> TwinResponse:
        """Fetch current authoritative digital twin state."""
        # For the demo, run a 0-day simulation to extract the latest twin state from the baseline
        config = SimulationConfig(
            simulation_id="demo_sim",
            seed=42,
            scenario_name="twin_state_sync",
            days=0,
            dt_hours=1.0,
            zones=self._demo_twin_zones
        )
        res = self.simulation_engine.run(config)
        twin = res.extra.get("final_twin")
        
        zones_resp = [
            ZoneResponse(zone_id=z.zone_id, crop_id=z.crop_id, area_sqm=z.area_sqm)
            for z in self._demo_twin_zones
        ]
        
        temp = 0.0
        hum = 0.0
        moisture = 0.0
        tank = 0.0
        
        if twin and twin.current_state:
            cs = twin.current_state
            if "temperature" in cs.environment:
                temp = cs.environment["temperature"].value
            if "humidity" in cs.environment:
                hum = cs.environment["humidity"].value
            moisture = cs.substrate_moisture.value if cs.substrate_moisture else 0.0
            tank = cs.tank_volume.value if cs.tank_volume else 0.0
            
        return TwinResponse(
            polyhouse_id="demo_polyhouse",
            zones=zones_resp,
            temperature_c=temp,
            humidity_percent=hum,
            substrate_moisture_percent=moisture,
            crop_stress_index=res.average_stress,
            tank_volume_l=tank,
            tank_capacity_l=5000.0,
            pump_state="OFF",
            sensor_health="HEALTHY",
            timestamp=time.time()
        )
        
    def get_resources(self) -> ResourceResponse:
        twin = self.get_twin_state()
        return ResourceResponse(
            tank_volume_l=twin.tank_volume_l,
            energy_kwh=100.0  # mock energy for now, as it's not dynamically simulated in baseline
        )
        
    def get_telemetry(self) -> list[TelemetryResponse]:
        # Return derived telemetry from the current twin state
        twin = self.get_twin_state()
        t = []
        for zone in twin.zones:
            t.append(TelemetryResponse(
                device_id=f"sensor_{zone.zone_id}_temp",
                zone_id=zone.zone_id,
                measurement_type="temperature",
                value=twin.temperature_c,
                unit="C",
                timestamp=twin.timestamp,
                quality=1.0
            ))
            t.append(TelemetryResponse(
                device_id=f"sensor_{zone.zone_id}_moist",
                zone_id=zone.zone_id,
                measurement_type="substrate_moisture",
                value=twin.substrate_moisture_percent,
                unit="%",
                timestamp=twin.timestamp,
                quality=1.0
            ))
        return t

    def submit_intent(self, req: IntentRequest) -> IntentResponse:
        """Run intent through IntentAgent and semantic validation."""
        # intent_agent is not returned, the intent is run directly
        structured_intent = self.agent_provider.run_intent_agent(req.text)
        
        plan_id = str(uuid.uuid4())
        
        # Simulate planning flow
        # In a real async flow, we would trigger the PlanningAgent here.
        # For the demo, we generate a mock valid plan proposal.
        proposal = ControlPlanProposal(
            actions=[],
            execution_status=ExecutionState.PROPOSED,
            created_by="planning_agent"
        )
        plan_repo.save(plan_id, proposal)
        
        return IntentResponse(
            objective=structured_intent.objective,
            constraints=structured_intent.constraints,
            target_zones=structured_intent.target_zones,
            plan_id=plan_id
        )
        
    def simulate(self, req: SimulationRequest) -> SimulationResponse:
        zones = []
        for z in req.zone_ids:
            # Try to map against our demo zones
            matched = next((dz for dz in self._demo_twin_zones if dz.zone_id == z), None)
            if matched:
                zones.append(matched)
                
        config = SimulationConfig(
            simulation_id=str(uuid.uuid4()),
            seed=42,
            scenario_name=req.scenario_name,
            days=req.days,
            dt_hours=req.dt_hours,
            zones=zones
        )
        res = self.simulation_engine.run(config)
        return self._map_simulation_result(res)
        
    def what_if(self, req: WhatIfRequest) -> WhatIfResponse:
        zones = []
        for z in req.zone_ids:
            matched = next((dz for dz in self._demo_twin_zones if dz.zone_id == z), None)
            if matched:
                zones.append(matched)
                
        baseline_config = SimulationConfig(
            simulation_id="baseline_id",
            seed=42,
            dt_hours=1.0,
            scenario_name="baseline",
            days=req.days,
            zones=zones
        )
        baseline_res = self.simulation_engine.run(baseline_config)
        
        # Build scenario
        scenario_zones = []
        for z_orig in zones:
            sz = ZoneSimConfig(
                zone_id=z_orig.zone_id, crop_id=z_orig.crop_id, area_sqm=z_orig.area_sqm, 
                plant_density_per_sqm=z_orig.plant_density_per_sqm, 
                initial_substrate_moisture=z_orig.initial_substrate_moisture, 
                initial_tank_volume_liters=z_orig.initial_tank_volume_liters
            )
            if req.water_availability_l is not None:
                # Divide water among zones for demo logic
                sz.initial_tank_volume_liters = req.water_availability_l / len(zones)
            scenario_zones.append(sz)
            
        scenario_config = SimulationConfig(
            simulation_id="scenario_id",
            seed=42,
            dt_hours=1.0,
            scenario_name="what_if_scenario",
            days=req.days,
            zones=scenario_zones
        )
        
        if req.temperature_bias_c is not None:
            scenario_config.initial_temperature_c += req.temperature_bias_c
            
        scenario_res = self.simulation_engine.run(scenario_config)
        
        return WhatIfResponse(
            baseline=self._map_simulation_result(baseline_res),
            scenario=self._map_simulation_result(scenario_res),
            delta_yield_kg=scenario_res.final_yield_kg - baseline_res.final_yield_kg,
            delta_water_used_l=scenario_res.water_used_l - baseline_res.water_used_l,
            delta_stress_index=scenario_res.stress_index - baseline_res.stress_index
        )
        
    def get_plan(self, plan_id: str) -> PlanResponse:
        plan = plan_repo.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        actions = []
        for a in plan.actions:
            actions.append(ActionResponse(
                zone_id=a.zone_id,
                actuator_id=a.actuator_id,
                action_type=a.action_type,
                target_value=a.target_value,
                duration_s=a.duration_s,
                reason=a.reason
            ))
            
        return PlanResponse(
            plan_id=plan_id,
            actions=actions,
            execution_status=plan.execution_status.value,
            created_by=plan.created_by
        )
        
    def approve_plan(self, plan_id: str, reason: str | None = None) -> PlanResponse:
        plan = plan_repo.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
            
        if plan.execution_status not in (ExecutionState.PROPOSED, ExecutionState.VALIDATED):
            raise ValueError(f"Invalid state transition from {plan.execution_status} to APPROVED")
            
        plan.execution_status = ExecutionState.APPROVED
        plan_repo.save(plan_id, plan)
        return self.get_plan(plan_id)
        
    def dispatch_plan(self, plan_id: str) -> ExecutionResponse:
        plan = plan_repo.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
            
        if plan.execution_status != ExecutionState.APPROVED:
            raise ValueError(f"Invalid state transition from {plan.execution_status} to DISPATCHED")
            
        plan.execution_status = ExecutionState.DISPATCHED
        plan_repo.save(plan_id, plan)
        
        execution_id = str(uuid.uuid4())
        execution_repo.save(execution_id, {
            "plan_id": plan_id,
            "status": "DISPATCHED",
            "dispatched_at": time.time(),
            "acknowledged_at": None
        })
        
        return ExecutionResponse(
            execution_id=execution_id,
            plan_id=plan_id,
            status="DISPATCHED",
            dispatched_at=time.time()
        )

physica_service = PhysicaApplicationService()
