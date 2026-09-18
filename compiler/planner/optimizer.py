"""
compiler/planner/optimizer.py

PHYSICA Optimizer layer.
Evaluates multiple candidate control policies by running them through
the SimulationEngine and computing an objective score.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from domains.polyhouse.controllers.baseline import (
    BaselineController,
    BaselineControlPolicy,
)
from domains.polyhouse.engine import (
    SimulationConfig,
    SimulationEngine,
    SimulationResult,
)


class ObjectiveWeights(BaseModel):
    yield_kg: float = 10.0      # High reward for yield
    water_l: float = -0.01      # Small penalty for water usage
    energy_kwh: float = -0.05   # Penalty for energy usage
    stress_penalty: float = -100.0 # Penalty for crop stress


class OptimizedPlan(BaseModel):
    policy_id: str
    score: float
    metrics: dict[str, Any]
    violations: list[str]
    is_safe: bool


class ScenarioOptimizer:
    """
    Optimizes a polyhouse scenario by evaluating candidate policies
    through the physical simulator.
    """

    def __init__(self, engine: SimulationEngine, weights: ObjectiveWeights | None = None) -> None:
        self.engine = engine
        self.weights = weights or ObjectiveWeights()

    def _compute_score(self, result: SimulationResult) -> float:
        # Objective = (Yield * w_yield) + (Water * w_water) + (Energy * w_energy) + (Stress * w_stress)
        score = 0.0
        score += result.final_yield_kg * self.weights.yield_kg
        score += result.total_water_liters * self.weights.water_l
        score += result.total_energy_kwh * self.weights.energy_kwh
        score += result.average_stress * self.weights.stress_penalty

        # Hard constraints (safety)
        if result.constraint_violations:
            score -= 10000.0 * len(result.constraint_violations)
            
        return score

    def optimize(self, base_config: SimulationConfig) -> OptimizedPlan:
        # Candidate policies to evaluate
        candidates = [
            BaselineControlPolicy(
                policy_id="baseline-standard",
                temp_band_c=2.0,
                humid_band_pct=5.0,
                moisture_band=5.0,
            ),
            BaselineControlPolicy(
                policy_id="baseline-water-saver",
                temp_band_c=2.0,
                humid_band_pct=5.0,
                moisture_band=10.0, # Allow drier substrate
            ),
            BaselineControlPolicy(
                policy_id="baseline-energy-saver",
                temp_band_c=4.0, # Allow more temp fluctuation
                humid_band_pct=10.0,
                moisture_band=5.0,
            ),
        ]

        best_plan: OptimizedPlan | None = None

        for policy in candidates:
            # Inject controller into engine
            self.engine.controller = BaselineController(policy=policy)
            
            # Run simulation
            # We copy config to ensure independence
            sim_config = base_config.model_copy(deep=True)
            result = self.engine.run(sim_config)
            
            score = self._compute_score(result)
            
            metrics = {
                "yield_kg": result.final_yield_kg,
                "water_l": result.total_water_liters,
                "energy_kwh": result.total_energy_kwh,
                "stress": result.average_stress,
            }
            
            plan = OptimizedPlan(
                policy_id=policy.policy_id,
                score=score,
                metrics=metrics,
                violations=result.constraint_violations,
                is_safe=len(result.constraint_violations) == 0,
            )
            
            if best_plan is None or plan.score > best_plan.score:
                best_plan = plan

        if best_plan is None:
            raise RuntimeError("Optimization failed: no valid policies found.")
        return best_plan
