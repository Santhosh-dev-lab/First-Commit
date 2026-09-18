from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from schemas.tools import SimulationResult, SafetyCheckResult


class FarmObjective(str, Enum):
    WATER_MINIMIZATION = "WATER_MINIMIZATION"
    STRESS_MINIMIZATION = "STRESS_MINIMIZATION"
    ENERGY_MINIMIZATION = "ENERGY_MINIMIZATION"
    YIELD_MAXIMIZATION = "YIELD_MAXIMIZATION"
    RESOURCE_CONSERVATION = "RESOURCE_CONSERVATION"
    BALANCED_OPERATION = "BALANCED_OPERATION"


class ObjectiveWeights(BaseModel):
    water_weight: float = Field(default=0.0, ge=0.0)
    stress_weight: float = Field(default=0.0, ge=0.0)
    energy_weight: float = Field(default=0.0, ge=0.0)
    yield_weight: float = Field(default=0.0, ge=0.0)


class CandidateStrategy(BaseModel):
    strategy_id: str
    policy_id: str
    name: str
    description: str
    parameters: dict[str, float] = Field(default_factory=dict)
    provenance: str = "system_generated"


class CandidateResult(BaseModel):
    candidate_id: str
    simulation_result: SimulationResult | None = None
    safety_result: SafetyCheckResult | None = None
    metrics: dict[str, float] = Field(default_factory=dict)
    score: float = 0.0
    status: str = "PENDING"  # PENDING, SAFE, REJECTED
    rejection_reason: str | None = None


class ExperimentRecord(BaseModel):
    experiment_id: str
    farm_id: str
    objective: FarmObjective
    objective_weights: ObjectiveWeights
    scenario: str
    seed: int
    baseline: CandidateResult | None = None
    candidates: list[CandidateResult] = Field(default_factory=list)
    selected_candidate_id: str | None = None
    selected_strategy: CandidateStrategy | None = None
    created_at: float
    simulation_metadata: dict[str, Any] = Field(default_factory=dict)
    execution_status: str = "EVALUATED"  # EVALUATED, EXECUTING, COMPLETED
    outcome: dict[str, Any] | None = None
