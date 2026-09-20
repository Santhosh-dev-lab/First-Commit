import hashlib
import time
import uuid
from typing import Any

from app.db.database import get_db
from app.services.physica_service import PhysicaApplicationService
from app.services.repositories import plan_repo
from core.safety.engine import SafetyVerifier
from domains.polyhouse.controllers.baseline import BaselineController
from domains.polyhouse.controllers.factory import get_policy
from domains.polyhouse.crops.registry import CropRegistry
from domains.polyhouse.engine import SimulationConfig, SimulationEngine, ZoneSimConfig
from schemas.autonomy import PlanningStateSnapshot
from schemas.experiments import (
    CandidateResult,
    CandidateStrategy,
    ExperimentRecord,
    FarmObjective,
    ObjectiveWeights,
)
from schemas.tools import ControlPlanProposal, SafetyCheckResult
from schemas.tools import SimulationResult as ToolsSimulationResult


# We'll use a global in-memory repository as requested
class InMemoryExperimentRepository:
    def __init__(self):
        self._experiments: dict[str, ExperimentRecord] = {}

    def save(self, record: ExperimentRecord):
        self._experiments[record.experiment_id] = record

    def get(self, experiment_id: str) -> ExperimentRecord | None:
        return self._experiments.get(experiment_id)

experiment_repo = InMemoryExperimentRepository()


class ExperimentService:
    def __init__(self, crop_registry: CropRegistry | None = None):
        self.crop_registry = crop_registry or CropRegistry.default()
        self.safety_verifier = SafetyVerifier.default(self.crop_registry)
        self.physica_service = PhysicaApplicationService()

    def generate_candidates(self, objective: FarmObjective) -> list[CandidateStrategy]:
        candidates = [
            CandidateStrategy(
                strategy_id=str(uuid.uuid4()),
                policy_id="BASELINE",
                name="Baseline Control",
                description="Existing production control policy"
            )
        ]
        
        base_id_prefix = objective.value.lower()
        idx = 1
        
        ADAPTIVE_IRRIGATION = {}
        REDUCED_IRRIGATION = {}
        PULSE_IRRIGATION = {}

        if objective in (FarmObjective.WATER_MINIMIZATION, FarmObjective.RESOURCE_CONSERVATION, FarmObjective.BALANCED_OPERATION):
            ADAPTIVE_IRRIGATION = {"1": {"stress_threshold": 0.4}}
            REDUCED_IRRIGATION = {"1": {"moisture_offset": -15.0}}
            PULSE_IRRIGATION = {"1": {"pulse_duration_s": 300.0}}
        elif objective == FarmObjective.STRESS_MINIMIZATION:
            ADAPTIVE_IRRIGATION = {"1": {"stress_threshold": 0.1}}

        for v in ADAPTIVE_IRRIGATION.values():
            candidates.append(CandidateStrategy(
                strategy_id=f"{base_id_prefix}_adaptive_{idx}",
                policy_id="ADAPTIVE_IRRIGATION",
                name=f"Adaptive (Stress < {v['stress_threshold']})",
                description=f"Irrigates when stress reaches {v['stress_threshold']}",
                parameters=v
            ))
            idx += 1

        for v in REDUCED_IRRIGATION.values():
            candidates.append(CandidateStrategy(
                strategy_id=f"{base_id_prefix}_reduced_{idx}",
                policy_id="REDUCED_IRRIGATION",
                name=f"Reduced (Offset {v['moisture_offset']}%)",
                description=f"Negative offset of {v['moisture_offset']}% to target moisture",
                parameters=v
            ))
            idx += 1

        for v in PULSE_IRRIGATION.values():
            candidates.append(CandidateStrategy(
                strategy_id=f"{base_id_prefix}_pulse_{idx}",
                policy_id="PULSE_IRRIGATION",
                name=f"Pulse ({v['pulse_duration_s']}s)",
                description=f"Short pulses of {v['pulse_duration_s']}s",
                parameters=v
            ))
            idx += 1
        
        return candidates

    def _get_farm_zones(self, farm_id: str) -> list[dict[str, Any]]:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM zones WHERE farm_id=?", (farm_id,))
        zones = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return zones

    def run_experiment(
        self, 
        farm_id: str, 
        objective: FarmObjective, 
        weights: ObjectiveWeights, 
        scenario: str,
        seed: int = 42,
        days: float = 7.0,
        snapshot: PlanningStateSnapshot | None = None
    ) -> ExperimentRecord:
        
        db_zones = self._get_farm_zones(farm_id)
        zone_configs = []
        for z in db_zones:
            tank_vol = 5000.0
            if snapshot and z["id"] in snapshot.resource_state.get("tank_volumes", {}):
                tank_vol = snapshot.resource_state["tank_volumes"][z["id"]]
            elif scenario == "DROUGHT":
                tank_vol = 0.0
                
            zone_configs.append(ZoneSimConfig(
                zone_id=z["id"],
                crop_id=z["crop_id"] or "dwarf_tomato",
                area_sqm=z["area_m2"],
                plant_density_per_sqm=5.0,
                initial_tank_volume_liters=tank_vol,
            ))

        candidates = self.generate_candidates(objective)
        
        # Fair comparison context
        if snapshot:
            initial_temp = snapshot.environment.get("temperature_c", 25.0)
            initial_hum = snapshot.environment.get("humidity_percent", 60.0)
            out_temp = snapshot.environment.get("outside_temperature_c", 22.0)
            out_hum = snapshot.environment.get("outside_humidity_percent", 50.0)
        else:
            initial_temp = 50.0 if scenario == "EXTREME_HEAT" else 25.0
            initial_hum = 60.0
            out_temp = 80.0 if scenario == "EXTREME_HEAT" else (30.0 if scenario == "WATER_SHORTAGE" else 22.0)
            out_hum = 50.0
            
        base_sim_config = SimulationConfig(
            simulation_id=f"sim-{uuid.uuid4().hex[:8]}",
            scenario_name=scenario,
            days=days,
            dt_hours=1.0,
            seed=seed,
            zones=zone_configs,
            initial_temperature_c=initial_temp,
            initial_humidity_percent=initial_hum,
            outside_temperature_c=out_temp,
            outside_humidity_percent=out_hum
        )

        candidate_results = []
        baseline_result = None

        for candidate in candidates:
            # Deep copy the config to ensure complete isolation
            config = base_sim_config.model_copy(deep=True)
            config.simulation_id = f"sim-{candidate.strategy_id}"
            
            policy = get_policy(candidate.policy_id, candidate.parameters)
            controller = BaselineController(policy=policy)
            engine = SimulationEngine(registry=self.crop_registry, controller=controller)
            
            sim_result = engine.run(config)
            
            # Safety filtering using SafetyVerifier on trajectory
            is_safe = True
            all_violations = []
            if "trajectory" in sim_result.extra:
                for step in sim_result.extra["trajectory"]:
                    state_dict = {
                        "temperature_c": step.temperature_c,
                        "humidity_percent": step.humidity_percent,
                        "co2_ppm": step.co2_ppm
                    }
                    for z_id, z_step in step.zones.items():
                        state_dict["substrate_moisture_percent"] = z_step.substrate_moisture_percent
                        # We use zone-level crop ID for safety checks
                        s_res = self.safety_verifier.verify(state_dict, zone_id=z_id, crop_id=z_step.crop_id)
                        if not s_res.is_safe:
                            is_safe = False
                            all_violations.extend([v.message for v in s_res.violations])
            
            # Also check if SimulationEngine reported constraint violations
            if sim_result.constraint_violations:
                is_safe = False
                all_violations.extend(sim_result.constraint_violations)

            safety_res = SafetyCheckResult(is_safe=is_safe, violations=list(set(all_violations)))
            
            # Deterministic Scoring
            # Normalization: lower is better for water, energy, stress. Higher is better for yield.
            max_water = 1000.0 * days * len(zone_configs)
            norm_water = min(1.0, sim_result.water_used_l / max_water) if max_water > 0 else 0.0
            
            norm_stress = min(1.0, sim_result.stress_index)
            
            max_energy = 50.0 * days
            norm_energy = min(1.0, sim_result.total_energy_kwh / max_energy) if max_energy > 0 else 0.0
            
            max_yield = 50.0 * days * len(zone_configs)
            norm_yield = min(1.0, sim_result.final_yield_kg / max_yield) if max_yield > 0 else 0.0

            # Calculate score (higher score is better)
            # Since water, stress, energy are costs, we subtract them or invert them.
            score = (
                weights.yield_weight * norm_yield
                - weights.water_weight * norm_water
                - weights.stress_weight * norm_stress
                - weights.energy_weight * norm_energy
            )
            
            # Additional penalty if water shortage is not met, but we keep it strictly on metrics
            metrics = {
                "water_used_l": sim_result.water_used_l,
                "stress_index": sim_result.stress_index,
                "total_energy_kwh": sim_result.total_energy_kwh,
                "final_yield_kg": sim_result.final_yield_kg,
                "score": score
            }

            status = "SAFE" if is_safe else "REJECTED"
            reason = "Violated constraints" if not is_safe else None

            tools_sim_res = ToolsSimulationResult(
                simulation_id=sim_result.simulation_id,
                total_days=sim_result.total_days_simulated,
                violations=sim_result.violations,
                stress_index=sim_result.stress_index,
                water_used_l=sim_result.water_used_l,
                requested_water_l=sim_result.requested_water_l,
                delivered_water_l=sim_result.delivered_water_l,
                unmet_water_demand_l=sim_result.unmet_water_demand_l,
                remaining_water_l=sim_result.remaining_water_l,
                yield_kg=sim_result.final_yield_kg
            )
            
            c_result = CandidateResult(
                candidate_id=candidate.strategy_id,
                simulation_result=tools_sim_res,
                safety_result=safety_res,
                metrics=metrics,
                score=score,
                status=status,
                rejection_reason=reason
            )
            
            if candidate.policy_id == "BASELINE":
                baseline_result = c_result
            candidate_results.append(c_result)

        # Selection (Deterministic, SAFE only)
        safe_candidates = [cr for cr in candidate_results if cr.status == "SAFE"]
        
        selected_candidate_id = None
        selected_strategy = None
        
        if safe_candidates:
            # Deterministic Tie-breaker:
            # 1. score (descending)
            # 2. water (ascending)
            # 3. stress (ascending)
            # 4. strategy_id (ascending string)
            safe_candidates.sort(key=lambda cr: (
                -cr.score,
                cr.metrics["water_used_l"],
                cr.metrics["stress_index"],
                cr.candidate_id
            ))
            selected_res = safe_candidates[0]
            selected_candidate_id = selected_res.candidate_id
            selected_strategy = next(c for c in candidates if c.strategy_id == selected_candidate_id)

        experiment = ExperimentRecord(
            experiment_id=str(uuid.uuid4()),
            farm_id=farm_id,
            objective=objective,
            objective_weights=weights,
            scenario=scenario,
            seed=seed,
            baseline=baseline_result,
            candidates=candidate_results,
            selected_candidate_id=selected_candidate_id,
            selected_strategy=selected_strategy,
            created_at=time.time(),
            simulation_metadata={
                "days": days,
                "zones": len(zone_configs),
                "crop_registry_hash": hashlib.md5(str(self.crop_registry).encode()).hexdigest()
            },
            execution_status="EVALUATED"
        )
        experiment_repo.save(experiment)
        return experiment

    def execute_selected_strategy(self, experiment_id: str, farm_id: str, user_id: str, execution_horizon_hours: float = 4.0) -> dict[str, Any]:
        experiment = experiment_repo.get(experiment_id)
        if not experiment:
            raise ValueError("Experiment not found")
            
        if experiment.farm_id != farm_id:
            raise ValueError("Unauthorized farm_id")
            
        if experiment.execution_status != "EVALUATED":
            raise ValueError("Experiment already executed or in progress")
            
        if not experiment.selected_strategy:
            raise ValueError("No safe strategy was selected")

        # Create control plan for the first execution window (e.g., 4 hours)
        policy = get_policy(experiment.selected_strategy.policy_id, experiment.selected_strategy.parameters)
        controller = BaselineController(policy=policy)
        
        db_zones = self._get_farm_zones(farm_id)
        from domains.polyhouse.controllers.base import ZoneControlContext
        
        # We need the real twin state for the actual ControlPlan
        # For simplicity in this milestone, we ask the runtime for contexts or simulate an instantaneous plan
        zone_contexts = []
        for z in db_zones:
            # Fetch latest telemetry for real context
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT measurements FROM telemetry_records WHERE farm_id=? AND zone_id=? ORDER BY timestamp DESC LIMIT 1", (farm_id, z["id"]))
            row = cursor.fetchone()
            conn.close()
            
            import json
            state = json.loads(row["measurements"]) if row else {}
            
            temp = state.get("temperature_c", 25.0)
            hum = state.get("humidity_percent", 60.0)
            co2 = state.get("co2_ppm", 400.0)
            moist = state.get("substrate_moisture_percent", 65.0)
            
            self.crop_registry.get(z["crop_id"])
            zone_contexts.append(ZoneControlContext(
                zone_id=z["id"],
                crop_id=z["crop_id"],
                temperature_c=temp,
                humidity_percent=hum,
                co2_ppm=co2,
                par_umol_m2_s=0.0,
                substrate_moisture_percent=moist,
                tank_volume_liters=10000.0,
                crop_age_days=10.0,
                crop_stage="VEGETATIVE",
                crop_stress_index=0.0,
                target_temperature_c=25.0,
                target_humidity_percent=60.0,
                target_moisture_percent=65.0,
                target_co2_ppm=400.0,
                target_par_umol_m2_s=400.0,
                water_available_l=10000.0,
                energy_available_kwh=99999.0
            ))
            
        plan = controller.plan(
            simulation_id="exec-" + experiment.experiment_id,
            timestep=0,
            time_days=0.0,
            zone_contexts=zone_contexts
        )
        
        proposal = ControlPlanProposal(
            farm_id=farm_id,
            actions=[
                {
                    "zone_id": a.zone_id,
                    "actuator_id": a.actuator_id,
                    "action_type": a.action_type.value,
                    "target_value": a.target_value,
                    "duration_s": a.duration_s,
                    "reason": f"[Experiment {experiment.selected_strategy.name}] {a.reason}"
                }
                for a in plan.actions
            ],
            created_by="experiment_engine"
        )
        
        plan_id = str(uuid.uuid4())
        plan_repo.save(plan_id, proposal)
        
        self.physica_service.approve_plan(plan_id, farm_id=farm_id)
        self.physica_service.dispatch_plan(plan_id, farm_id=farm_id)
        
        experiment.execution_status = "EXECUTED"
        experiment.outcome = {"dispatched_plan_id": plan_id, "execution_horizon_hours": execution_horizon_hours}
        experiment_repo.save(experiment)
        
        return {"status": "SUCCESS", "plan_id": plan_id}
