from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# --- Tools Schemas ---

class SimulationRequest(BaseModel):
    scenario_name: str = Field(description="Name of the scenario being simulated")
    days: int = Field(description="Number of days to simulate")
    dt_hours: float = Field(default=1.0, description="Timestep in hours")
    zone_ids: list[str] = Field(description="List of zones to simulate")
    
class SimulationResult(BaseModel):
    simulation_id: str
    total_days: float
    violations: int
    stress_index: float
    water_used_l: float
    requested_water_l: float = 0.0
    delivered_water_l: float = 0.0
    unmet_water_demand_l: float = 0.0
    remaining_water_l: float = 0.0
    yield_kg: float

class ExecutionState(str, Enum):
    PROPOSED = "PROPOSED"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    DISPATCHED = "DISPATCHED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    OBSERVED = "OBSERVED"
    FAILED = "FAILED"
    UNCERTAIN = "UNCERTAIN"
    REJECTED = "REJECTED"

class OptimizationRequest(BaseModel):
    days: int = Field(description="Horizon in days")
    zone_id: str = Field(description="Zone to optimize")
    
class OptimizationResult(BaseModel):
    policy_id: str
    is_safe: bool
    score: float
    metrics: dict[str, float]

class ControlActionProposal(BaseModel):
    zone_id: str = Field(description="Target zone identifier")
    actuator_id: str = Field(description="Target actuator identifier (e.g., pump-1, vent-top)")
    action_type: str = Field(description="Action to perform (e.g., SET, INCREASE, DECREASE)")
    target_value: float = Field(description="Target value or setpoint")
    duration_s: float = Field(description="Duration in seconds (0 for indefinite)")
    reason: str = Field(description="Agent's reasoning for this action")

class ControlPlanProposal(BaseModel):
    actions: list[ControlActionProposal] = Field(description="List of proposed actions")
    execution_status: ExecutionState = Field(default=ExecutionState.PROPOSED)
    created_by: str = Field(default="planning_agent")
    
class SafetyCheckResult(BaseModel):
    is_safe: bool
    violations: list[str]

# --- Agent Schemas ---

class StructuredIntent(BaseModel):
    objective: str
    constraints: list[str]
    target_zones: list[str]

class AgentContext(BaseModel):
    farm_id: str = "default_farm"
    polyhouse_id: str = "default_polyhouse"
    zone_ids: list[str] = Field(default_factory=list)
    crop_ids: list[str] = Field(default_factory=list)
    twin_snapshot_id: str = ""
    context_hash: str = ""
    timestamp: float = 0.0
    autonomy_level: int = 1

class Evidence(BaseModel):
    observed: list[str] = Field(default_factory=list)
    computed: list[str] = Field(default_factory=list)
    assumed: list[str] = Field(default_factory=list)
    configured: list[str] = Field(default_factory=list)
    predicted: list[str] = Field(default_factory=list)
    simulated: list[str] = Field(default_factory=list)

class AgentTrace(BaseModel):
    agent_run_id: str
    agent_type: str
    agent_version: str = "1.0"
    prompt_version: str = "1.0"
    model_provider: str = "strands"
    model_id: str = "default"
    timestamp: float
    input_context_hash: str = ""
    tools_called: list[str] = Field(default_factory=list)
    tool_inputs: dict[str, Any] = Field(default_factory=dict)
    tool_outputs: dict[str, Any] = Field(default_factory=dict)
    final_structured_output: Any = None
    decision: str = ""
    evidence: Evidence | None = None
    safety_result: SafetyCheckResult | None = None
    approval_status: str = "PENDING"
    execution_status: str = "PROPOSED"
    errors: list[str] = Field(default_factory=list)
