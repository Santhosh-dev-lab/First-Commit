from __future__ import annotations

import json
import time
import uuid
from typing import Any

from agents.base import MockAgentProvider
from app.api.schemas import (
    ActionResponse,
    DashboardSnapshot,
    ExecutionResponse,
    IntentRequest,
    IntentResponse,
    PlanResponse,
    ResourceSummary,
    SimulationRequest,
    SimulationResponse,
    SystemStatus,
    TelemetryResponse,
    WhatIfRequest,
    WhatIfResponse,
    ZoneSummary,
)
from app.db.database import get_db
from app.services.farm_service import FarmService
from app.services.gateway_factory import gateway_factory
from app.services.repositories import execution_repo, plan_repo
from core.safety.engine import SafetyVerifier
from domains.polyhouse.crops.registry import CropRegistry
from domains.polyhouse.engine import SimulationConfig, SimulationEngine
from schemas.tools import (
    ControlPlanProposal,
    ExecutionState,
)


class PhysicaApplicationService:
    def __init__(self) -> None:
        self.crop_registry = CropRegistry.default()
        self.simulation_engine = SimulationEngine(registry=self.crop_registry)
        self.safety_verifier = SafetyVerifier.default(registry=self.crop_registry)
        self.agent_provider = MockAgentProvider()
        
        self._last_tick = {} # map farm_id -> last_tick time
        
    def _tick_simulation_for_farm(self, farm_data: dict):
        """Advances the local simulation for a farm and routes telemetry to ingestion."""
        from app.services.telemetry_ingestion import telemetry_ingestion_service
        from domains.edge.models import TelemetryEnvelope, TelemetrySource

        farm_id = farm_data["farm"]["id"]
        now = time.time()
        last_tick = self._last_tick.get(farm_id, now)
        dt = now - last_tick
        self._last_tick[farm_id] = now
        
        if dt <= 0:
            return
            
        conn = get_db()
        cursor = conn.cursor()
        
        for z in farm_data["zones"]:
            zone_id = z["id"]
            cursor.execute("SELECT measurements FROM telemetry_records WHERE farm_id=? AND zone_id=? ORDER BY timestamp DESC LIMIT 1", (farm_id, zone_id))
            row = cursor.fetchone()
            
            moisture = 65.0
            temp = 24.1
            if row:
                try:
                    meas = json.loads(row['measurements'])
                    moisture = meas.get("substrate_moisture", 65.0)
                    temp = meas.get("temperature_c", 24.1)
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass
                    
            moisture = max(0.0, moisture - (0.05 * dt)) # dry out
            
            envelope = TelemetryEnvelope(
                farm_id=farm_id,
                gateway_id="LOCAL_GW",
                device_id=f"sim_sensor_{zone_id}",
                zone_id=zone_id,
                timestamp=now,
                source=TelemetrySource.LOCAL_SIMULATION,
                measurements={
                    "substrate_moisture": moisture,
                    "temperature_c": temp,
                    "humidity_percent": 68.0,
                    "crop_stress_index": 0.12
                }
            )
            
            telemetry_ingestion_service.process_telemetry(envelope)
            
        conn.commit()
        conn.close()

    def get_dashboard_snapshot(self, farm_id: str) -> DashboardSnapshot:
        farm_data = FarmService.get_farm_by_id(farm_id)
        if not farm_data:
            raise ValueError(f"Farm {farm_id} not found")
            
        farm = farm_data["farm"]
        farm_id = farm["id"]
        connection = farm_data.get("connection") or {}
        conn_mode = connection.get("mode", "CONNECT_LATER")
        
        if conn_mode == "LOCAL_SIMULATION":
            self._tick_simulation_for_farm(farm_data)
            
        # Fetch latest telemetry per zone
        zones_summary = []
        conn = get_db()
        cursor = conn.cursor()
        
        for z in farm_data["zones"]:
            cursor.execute("SELECT measurements FROM telemetry_records WHERE farm_id=? AND zone_id=? ORDER BY timestamp DESC LIMIT 1", (farm_id, z['id']))
            row = cursor.fetchone()
            moisture = 0.0
            temp = 0.0
            hum = 0.0
            stress = 0.0
            status = "OFFLINE"
            
            if row:
                try:
                    meas = json.loads(row['measurements'])
                    moisture = meas.get("substrate_moisture", 0.0)
                    temp = meas.get("temperature_c", 0.0)
                    hum = meas.get("humidity_percent", 0.0)
                    stress = meas.get("crop_stress_index", 0.0)
                    status = "ONLINE"
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass
                    
            zones_summary.append(ZoneSummary(
                zone_id=z['name'], # UI expects name here based on demo
                crop_id=z['crop_id'] or "unknown",
                area_sqm=z['area_m2'],
                growth_stage=z['growth_stage'] or "Unknown",
                temperature_c=temp,
                humidity_percent=hum,
                moisture_percent=moisture,
                stress_index=stress,
                irrigation_status="IDLE",
                sensor_health="HEALTHY" if status == "ONLINE" else "UNKNOWN",
                status=status
            ))
            
        conn.close()
        
        resources_db = farm_data.get("resources") or {}
        resources = ResourceSummary(
            tank_volume_l=resources_db.get("tank_capacity_l", 0.0),
            requested_water_l=0.0,
            delivered_water_l=0.0,
            unmet_water_demand_l=0.0,
            remaining_water_l=resources_db.get("tank_capacity_l", 0.0)
        )
        
        system = SystemStatus(
            is_online=connection.get("status") == "CONNECTED",
            physical_mode=conn_mode,
            agent_provider="MOCK",
            digital_twin="SYNCHRONIZED" if connection.get("status") == "CONNECTED" else "WAITING",
            safety="AVAILABLE",
            last_sync_timestamp=time.time(),
            farm_name=farm['name']
        )
        
        # Build telemetry history for the chart
        raw_telemetry = FarmService.get_latest_telemetry(farm_id, limit=50)
        formatted_telemetry = []
        for t in raw_telemetry:
            meas = t.get("measurements", {})
            for key, val in meas.items():
                unit = "%" if "moisture" in key or "humidity" in key else "C" if "temp" in key else ""
                formatted_telemetry.append(
                    TelemetryResponse(
                        device_id=t["device_id"],
                        zone_id=t["zone_id"],
                        measurement_type=key,
                        value=float(val),
                        unit=unit,
                        timestamp=t["timestamp"],
                        quality=1.0
                    )
                )
        
        # Get active plans
        all_plans = plan_repo.get_all()
        active_plans = []
        for p_id in all_plans:
            try:
                active_plans.append(self.get_plan(p_id, farm_id))
            except (ValueError, KeyError):
                pass
        
        return DashboardSnapshot(
            system=system,
            zones=zones_summary,
            resources=resources,
            telemetry=formatted_telemetry,
            alerts=[],
            agent_trace=None,
            active_plans=active_plans
        )


    def submit_intent(self, req: IntentRequest, farm_id: str) -> IntentResponse:
        """Run intent through IntentAgent and semantic validation."""
        structured_intent = self.agent_provider.run_intent_agent(req.text)
        plan_result = self.agent_provider.run_planning_agent(structured_intent)
        
        plan_id = str(uuid.uuid4())
        
        proposal = plan_result["control_plan"]
        proposal.farm_id = farm_id
        
        plan_repo.save(plan_id, proposal)
        
        return IntentResponse(
            objective=structured_intent.objective,
            constraints=structured_intent.constraints,
            target_zones=structured_intent.target_zones,
            plan_id=plan_id
        )
        
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

    def simulate(self, req: SimulationRequest) -> SimulationResponse:
        # Simplified for refactor
        config = SimulationConfig(
            simulation_id=str(uuid.uuid4()),
            seed=42,
            scenario_name=req.scenario_name,
            days=req.days,
            dt_hours=req.dt_hours,
            zones=[]
        )
        res = self.simulation_engine.run(config)
        return self._map_simulation_result(res)
        
    def what_if(self, req: WhatIfRequest) -> WhatIfResponse:
        raise NotImplementedError("what_if is currently disconnected pending refactor")
        
    def get_plan(self, plan_id: str, farm_id: str) -> PlanResponse:
        plan = plan_repo.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        if plan.farm_id != farm_id:
            raise ValueError(f"Plan {plan_id} not found") # IDOR protection
        
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
        
    def validate_plan_safety(self, plan: ControlPlanProposal, farm_id: str) -> bool:
        # Fetch latest state from digital twin (telemetry_records)
        conn = get_db()
        cursor = conn.cursor()
        
        # We need a unified state for the safety verifier. We'll average or take the latest zone state.
        # For simplicity, if any zone is unsafe, we reject the plan.
        is_safe = True
        violations = []
        for action in plan.actions:
            zone_id = action.zone_id
            cursor.execute("SELECT measurements FROM telemetry_records WHERE farm_id=? AND zone_id=? ORDER BY timestamp DESC LIMIT 1", (farm_id, zone_id))
            row = cursor.fetchone()
            state = {}
            if row:
                try:
                    state = json.loads(row['measurements'])
                except:
                    pass
            
            # Fetch crop_id for the zone
            cursor.execute("SELECT crop_id FROM zones WHERE id=? AND farm_id=?", (zone_id, farm_id))
            crop_row = cursor.fetchone()
            crop_id = crop_row["crop_id"] if crop_row else None
            
            result = self.safety_verifier.verify(state, zone_id=zone_id, crop_id=crop_id)
            if not result.is_safe:
                is_safe = False
                violations.extend(result.violations)
                break
                
        conn.close()
        
        if not is_safe:
            plan.execution_status = ExecutionState.REJECTED
            return False
            
        return True

    def approve_plan(self, plan_id: str, farm_id: str, reason: str | None = None) -> PlanResponse:
        plan = plan_repo.get(plan_id)
        if not plan or plan.farm_id != farm_id:
            raise ValueError(f"Plan {plan_id} not found")
            
        if plan.execution_status not in (ExecutionState.PROPOSED, ExecutionState.VALIDATED):
            raise ValueError(f"Invalid state transition from {plan.execution_status} to APPROVED")
            
        if not self.validate_plan_safety(plan, farm_id):
            plan_repo.save(plan_id, plan)
            raise ValueError("Plan rejected by SafetyEngine due to safety violations")
            
        plan.execution_status = ExecutionState.APPROVED
        plan_repo.save(plan_id, plan)
        return self.get_plan(plan_id, farm_id)
        
    def dispatch_plan(self, plan_id: str, farm_id: str) -> ExecutionResponse:
        plan = plan_repo.get(plan_id)
        if not plan or plan.farm_id != farm_id:
            raise ValueError(f"Plan {plan_id} not found")
            
        if plan.execution_status != ExecutionState.APPROVED:
            raise ValueError(f"Invalid state transition from {plan.execution_status} to DISPATCHED")
            
        conn = get_db()
        cursor = conn.cursor()
        
        # Validate device capabilities
        for action in plan.actions:
            cursor.execute("SELECT device_type FROM devices WHERE id = ? AND farm_id = ?", (action.actuator_id, farm_id))
            row = cursor.fetchone()
            if not row:
                conn.close()
                raise ValueError(f"Device {action.actuator_id} not found on farm")
            
            dev_type = row["device_type"]
            # Enforce Command Capability matches
            if action.action_type.startswith("PUMP_") and dev_type != "PUMP":
                conn.close()
                raise ValueError(f"Device {action.actuator_id} ({dev_type}) cannot execute PUMP commands")
            if action.action_type.startswith("VALVE_") and dev_type != "VALVE":
                conn.close()
                raise ValueError(f"Device {action.actuator_id} ({dev_type}) cannot execute VALVE commands")
            if action.action_type.startswith("VENT_") and dev_type != "VENT":
                conn.close()
                raise ValueError(f"Device {action.actuator_id} ({dev_type}) cannot execute VENT commands")
                
        conn.close()
            
        plan.execution_status = ExecutionState.DISPATCHED
        plan_repo.save(plan_id, plan)
        
        execution_id = str(uuid.uuid4())
        execution_record = {
            "plan_id": plan_id,
            "farm_id": farm_id,
            "status": "DISPATCHED",
            "dispatched_at": time.time(),
            "acknowledged_at": None,
            "observed_at": None
        }
        execution_repo.save(execution_id, execution_record)
        
        # Get connection mode
        farm_data = FarmService.get_user_farm("admin") # Hack since we don't pass user_id here, but we can query DB
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT mode FROM farm_connections WHERE farm_id=?", (farm_id,))
        row = cursor.fetchone()
        conn.close()
        
        connection_mode = row["mode"] if row else "LOCAL_SIMULATION"
        gateway = gateway_factory.create_gateway(farm_id, connection_mode)
        
        from domains.edge.models import CommandEnvelope, CommandType
        
        for action in plan.actions:
            command_id = f"cmd_{execution_id}_{action.actuator_id}"
            
            # map action type
            cmd_type = CommandType.PUMP_ON
            if action.action_type == "SET_ON" and "pump" in action.actuator_id.lower():
                cmd_type = CommandType.PUMP_ON
            elif action.action_type == "SET_OFF" and "pump" in action.actuator_id.lower():
                cmd_type = CommandType.PUMP_OFF
            elif action.action_type == "SET_ON" and "vent" in action.actuator_id.lower():
                cmd_type = CommandType.VENT_OPEN
            elif action.action_type == "SET_OFF" and "vent" in action.actuator_id.lower():
                cmd_type = CommandType.VENT_CLOSE
            elif action.action_type == "SET_ON" and "valve" in action.actuator_id.lower():
                cmd_type = CommandType.VALVE_OPEN
            elif action.action_type == "SET_OFF" and "valve" in action.actuator_id.lower():
                cmd_type = CommandType.VALVE_CLOSE
            else:
                cmd_type = CommandType.PUMP_ON # Fallback
            
            envelope = CommandEnvelope(
                command_id=command_id,
                farm_id=farm_id,
                gateway_id=f"gw_{farm_id}",
                device_id=action.actuator_id,
                timestamp=time.time(),
                command_type=cmd_type,
                parameters={"target_value": action.target_value, "duration_s": action.duration_s}
            )
            gateway.send_command(envelope)
            
            # Since the command was sent successfully, we rely on the gateway to mark ACKNOWLEDGED, 
            # but for tests, if it's synchronous local we might see it right away. 
            # Actually, Rule 1 says: "Gateway.send_command() -> gateway accepts command -> ExecutionRepository transition to ACKNOWLEDGED".
            # VirtualEdgeGateway should update execution_repo, not us.
        
        return ExecutionResponse(
            execution_id=execution_id,
            plan_id=plan_id,
            status="DISPATCHED",
            dispatched_at=time.time()
        )

physica_service = PhysicaApplicationService()
