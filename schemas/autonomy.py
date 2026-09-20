from typing import Any

from pydantic import BaseModel, Field

from schemas.experiments import (
    CandidateResult,
    CandidateStrategy,
    FarmObjective,
    ObjectiveWeights,
)


class PlanningHorizon(BaseModel):
    planning_duration_hours: float = Field(default=24.0, gt=0.0)
    execution_duration_hours: float = Field(default=4.0, gt=0.0)
    replanning_interval_hours: float = Field(default=4.0, gt=0.0)
    simulation_step_hours: float = Field(default=1.0, gt=0.0)


class PlanningStateSnapshot(BaseModel):
    farm_id: str
    timestamp: float
    environment: dict[str, Any] = Field(default_factory=dict)
    zones: list[dict[str, Any]] = Field(default_factory=list)
    resource_state: dict[str, Any] = Field(default_factory=dict)
    device_state: dict[str, Any] = Field(default_factory=dict)
    active_scenario: str | None = None


class AutonomyCycle(BaseModel):
    cycle_id: str
    run_id: str
    cycle_number: int
    state_snapshot: PlanningStateSnapshot
    candidate_results: list[CandidateResult] = Field(default_factory=list)
    selected_candidate_id: str | None = None
    selected_strategy: CandidateStrategy | None = None
    control_plan_id: str | None = None
    execution_id: str | None = None
    acknowledgement_status: str = "PENDING"
    observation_status: str = "PENDING"
    observed_outcome: dict[str, float] | None = None
    strategy_changed: bool = False
    created_at: float


class AutonomyRun(BaseModel):
    run_id: str
    farm_id: str
    objective: FarmObjective
    objective_weights: ObjectiveWeights
    planning_horizon: PlanningHorizon
    status: str = "ACTIVE"
    current_cycle: int = 0
    started_at: float
    last_cycle_at: float | None = None
    current_strategy: str | None = None
    total_water_used: float = 0.0
    current_stress: float = 0.0
    current_energy: float = 0.0
    remaining_resources: dict[str, float] = Field(default_factory=dict)
