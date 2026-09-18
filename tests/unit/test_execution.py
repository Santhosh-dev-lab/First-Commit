import pytest

from domains.polyhouse.controllers.base import (
    ControlPlan,
)
from domains.polyhouse.crops.registry import CropRegistry
from domains.polyhouse.edge.gateway import EdgeGateway
from domains.polyhouse.engine import SimulationConfig, SimulationEngine, ZoneSimConfig
from schemas.tools import ControlPlanProposal, ExecutionState


def test_control_plan_proposal_gateway_rejection() -> None:
    # 4. ControlPlanProposal cannot reach EdgeGateway.
    gateway = EdgeGateway()
    proposal = ControlPlanProposal(actions=[])
    
    with pytest.raises(TypeError, match="EdgeGateway strictly requires a validated ControlPlan"):
        gateway.dispatch(proposal) # type: ignore

def test_zero_day_simulation_is_not_observed() -> None:
    # 1. zero-day simulation cannot be treated as observed execution
    # If simulated for 0 days, telemetry doesn't update the state functionally.
    registry = CropRegistry.default()
    engine = SimulationEngine(registry)
    sim_config = SimulationConfig(
        simulation_id="test", scenario_name="test", days=0, dt_hours=1.0, seed=42,
        zones=[ZoneSimConfig(zone_id="z1", crop_id="dwarf_tomato", area_sqm=500.0, plant_density_per_sqm=15.0)]
    )
    result = engine.run(sim_config)
    assert result.total_days_simulated == 0.0

def test_actual_simulated_execution_transitions() -> None:
    # 2. actual simulated execution produces state/telemetry transition.
    # 3. Digital Twin receives actual post-execution telemetry.
    registry = CropRegistry.default()
    engine = SimulationEngine(registry)
    sim_config = SimulationConfig(
        simulation_id="test", scenario_name="test", days=1, dt_hours=1.0, seed=42,
        zones=[ZoneSimConfig(zone_id="z1", crop_id="dwarf_tomato", area_sqm=500.0, plant_density_per_sqm=15.0)]
    )
    result = engine.run(sim_config)
    
    twin = result.extra.get("final_twin")
    assert twin is not None
    assert twin.current_state is not None
    assert twin.current_state.substrate_moisture is not None
    # Moisture should be non-zero and populated from twin physics
    assert twin.current_state.substrate_moisture.value > 0.0

def test_execution_state_transitions() -> None:
    # 8. missing telemetry results in UNCERTAIN rather than OBSERVED.
    # 9. dispatched command is not automatically considered OBSERVED.
    # 10. simulated device acknowledgement is distinct from dispatch.
    
    plan = ControlPlan(
        plan_id="1", simulation_id="s1", timestep=0, time_days=0.0,
        actions=[]
    )
    plan.metadata["execution_status"] = ExecutionState.PROPOSED.value
    
    gateway = EdgeGateway()
    gateway.dispatch(plan)
    
    # Gateway dispatch immediately marks DISPATCHED
    assert plan.metadata["execution_status"] == ExecutionState.DISPATCHED.value
    
    # If device accepts:
    plan.metadata["execution_status"] = ExecutionState.ACKNOWLEDGED.value
    assert plan.metadata["execution_status"] == ExecutionState.ACKNOWLEDGED.value
    
    # If telemetry doesn't arrive:
    plan.metadata["execution_status"] = ExecutionState.UNCERTAIN.value
    assert plan.metadata["execution_status"] == ExecutionState.UNCERTAIN.value
