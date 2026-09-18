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
            ZoneSimConfig(zone_id="zone_1", crop_id="dwarf_tomato", area_sqm=500.0, plant_density_per_sqm=10.0, initial_substrate_moisture=65.0, initial_tank_volume_liters=2500.0),
            ZoneSimConfig(zone_id="zone_2", crop_id="lettuce", area_sqm=300.0, plant_density_per_sqm=15.0, initial_substrate_moisture=70.0, initial_tank_volume_liters=2500.0)
        ]
        
        # Persistent interactive demo state
        self._last_tick = time.time()
        self._persistent_state = {
            "tank_volume_l": 5000.0,
            "pump_state": "IDLE",
            "zones": {
                "zone_1": {"moisture": 65.0, "temp": 24.1, "hum": 68.0, "stress": 0.12},
                "zone_2": {"moisture": 70.0, "temp": 23.5, "hum": 66.0, "stress": 0.08}
            },
            "alerts": [],
            "telemetry_history": [],
            "total_water_requested": 0.0,
            "total_water_delivered": 0.0,
            "total_water_unmet": 0.0,
        }
        
    def _tick_state(self):
        now = time.time()
        dt = now - self._last_tick
        self._last_tick = now
        
        # Very simple physical evolution
        for z_id, z_state in self._persistent_state["zones"].items():
            # Dry out slightly over time
            z_state["moisture"] = max(0.0, z_state["moisture"] - (0.01 * dt))
            
            if self._persistent_state["pump_state"] == "ON":
                flow = 50.0 * dt # L/s
                if self._persistent_state["tank_volume_l"] > flow:
                    self._persistent_state["tank_volume_l"] -= flow
                    z_state["moisture"] = min(100.0, z_state["moisture"] + (0.5 * dt))
                    self._persistent_state["total_water_delivered"] += flow
                    self._persistent_state["total_water_requested"] += flow
                else:
                    self._persistent_state["total_water_requested"] += flow
                    self._persistent_state["total_water_unmet"] += flow
                    self._persistent_state["pump_state"] = "IDLE"
                    
            # Record telemetry occasionally (e.g. 1 per second max to avoid bloat)
            if not self._persistent_state["telemetry_history"] or (now - self._persistent_state["telemetry_history"][-1].timestamp > 1.0):
                self._persistent_state["telemetry_history"].append(
                    TelemetryResponse(
                        device_id=f"sensor_{z_id}_moist",
                        zone_id=z_id,
                        measurement_type="substrate_moisture",
                        value=z_state["moisture"],
                        unit="%",
                        timestamp=now,
                        quality=1.0
                    )
                )
                
        # Trim history
        if len(self._persistent_state["telemetry_history"]) > 100:
             self._persistent_state["telemetry_history"] = self._persistent_state["telemetry_history"][-100:]
        
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
        self._tick_state()
        now = time.time()
        
        zones_resp = [
            ZoneResponse(zone_id=z.zone_id, crop_id=z.crop_id, area_sqm=z.area_sqm)
            for z in self._demo_twin_zones
        ]
        
        avg_temp = sum(z["temp"] for z in self._persistent_state["zones"].values()) / len(self._persistent_state["zones"])
        avg_hum = sum(z["hum"] for z in self._persistent_state["zones"].values()) / len(self._persistent_state["zones"])
        avg_moist = sum(z["moisture"] for z in self._persistent_state["zones"].values()) / len(self._persistent_state["zones"])
        avg_stress = sum(z["stress"] for z in self._persistent_state["zones"].values()) / len(self._persistent_state["zones"])

        return TwinResponse(
            polyhouse_id="demo_polyhouse",
            zones=zones_resp,
            temperature_c=avg_temp,
            humidity_percent=avg_hum,
            substrate_moisture_percent=avg_moist,
            crop_stress_index=avg_stress,
            tank_volume_l=self._persistent_state["tank_volume_l"],
            tank_capacity_l=5000.0,
            pump_state=self._persistent_state["pump_state"],
            sensor_health="HEALTHY",
            timestamp=now
        )
        
    def get_resources(self) -> ResourceResponse:
        self._tick_state()
        return ResourceResponse(
            tank_volume_l=self._persistent_state["tank_volume_l"],
            energy_kwh=100.0
        )
        
    def get_telemetry(self) -> list[TelemetryResponse]:
        self._tick_state()
        return self._persistent_state["telemetry_history"]
        
    def get_dashboard_snapshot(self, user_id: str) -> Any:
        from app.api.schemas import (
            DashboardSnapshot, SystemStatus, ZoneSummary, ResourceSummary, AlertSummary, PlanResponse
        )
        from app.db.database import get_db
        
        self._tick_state()
        now = time.time()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Load farm
        cursor.execute("SELECT id, name FROM farms WHERE user_id = ?", (user_id,))
        farm = cursor.fetchone()
        
        zones_summary = []
        resources = ResourceSummary(
            tank_volume_l=0.0,
            requested_water_l=0.0,
            delivered_water_l=0.0,
            unmet_water_demand_l=0.0,
            remaining_water_l=0.0
        )
        
        if farm:
            farm_id = farm['id']
            # Load env
            cursor.execute("SELECT id FROM environments WHERE farm_id = ?", (farm_id,))
            env = cursor.fetchone()
            
            if env:
                env_id = env['id']
                # Load zones
                cursor.execute("SELECT id, name, area_sqm, crop_id, growth_stage FROM zones WHERE environment_id = ?", (env_id,))
                db_zones = cursor.fetchall()
                
                for z in db_zones:
                    # Map to persistent state (demo fallback)
                    state = self._persistent_state["zones"].get(z['id'], {"temp": 24.0, "hum": 60.0, "moisture": 65.0, "stress": 0.05})
                    zones_summary.append(ZoneSummary(
                        zone_id=z['id'],
                        crop_id=z['crop_id'] or "unknown",
                        area_sqm=z['area_sqm'],
                        growth_stage=z['growth_stage'] or "Unknown",
                        temperature_c=state["temp"],
                        humidity_percent=state["hum"],
                        moisture_percent=state["moisture"],
                        stress_index=state["stress"],
                        irrigation_status=self._persistent_state["pump_state"],
                        sensor_health="HEALTHY",
                        status="ONLINE",
                        # We inject name into zone_id field for UI display or pass it directly if we modify the schema
                    ))
                    # For the dashboard demo, we want to show the REAL name from DB:
                    zones_summary[-1].zone_id = z['name'] 

                # Load resources
                cursor.execute("SELECT tank_capacity_l, current_water_l FROM resources WHERE environment_id = ?", (env_id,))
                res = cursor.fetchone()
                if res:
                    resources.tank_volume_l = res['tank_capacity_l'] or 0.0
                    resources.remaining_water_l = res['current_water_l'] or 0.0
                    # For the demo, use global state for flow metrics
                    resources.requested_water_l = self._persistent_state["total_water_requested"]
                    resources.delivered_water_l = self._persistent_state["total_water_delivered"]
                    resources.unmet_water_demand_l = self._persistent_state["total_water_unmet"]
                    
        conn.close()
        
        system = SystemStatus(
            is_online=True,
            physical_mode="SIMULATION",
            agent_provider="MOCK",
            digital_twin="SYNCHRONIZED",
            safety="AVAILABLE",
            last_sync_timestamp=now,
            farm_name=farm['name'] if farm else "Unknown Farm"
        )
        
        # Get active plans
        all_plans = plan_repo.get_all()
        active_plans = [self.get_plan(p_id) for p_id in all_plans.keys()]
        
        return DashboardSnapshot(
            system=system,
            zones=zones_summary,
            resources=resources,
            telemetry=self._persistent_state["telemetry_history"],
            alerts=self._persistent_state["alerts"],
            agent_trace=None,
            active_plans=active_plans
        )


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
        
        # EFFECT: Change persistent state based on dispatched plan actions
        for a in plan.actions:
            if a.actuator_id.startswith("pump"):
                self._persistent_state["pump_state"] = "ON" if a.action_type == "SET_ON" else "IDLE"
        
        return ExecutionResponse(
            execution_id=execution_id,
            plan_id=plan_id,
            status="DISPATCHED",
            dispatched_at=time.time()
        )

physica_service = PhysicaApplicationService()
