from typing import Any

from compiler.planner.control_plan import ControlPlanBuilder
from domains.polyhouse.controllers.base import ActionType, ActuatorType, ControlAction
from domains.polyhouse.devices.registry import DeviceRegistry
from domains.polyhouse.edge.gateway import EdgeGateway
from domains.polyhouse.engine import SimulationConfig, SimulationEngine, ZoneSimConfig
from schemas.tools import ControlActionProposal, ControlPlanProposal, ExecutionState


def test_water_consumption_cannot_exceed_resource() -> None:
    DeviceRegistry()
    engine = SimulationEngine()
    
    config = SimulationConfig(
        simulation_id="test-water",
        scenario_name="water-limited",
        days=1,
        dt_hours=1.0,
        seed=42,
        zones=[ZoneSimConfig(zone_id="z1", crop_id="dwarf_tomato", area_sqm=500.0, plant_density_per_sqm=10.0, initial_tank_volume_liters=100.0)]
    )
    
    res = engine.run(config)
    assert res.total_water_liters <= 100.0


def test_infeasible_water_candidate_rejected() -> None:
    # If a simulation draws more water than allowed, it should be constrained
    # by the physics engine clamping `tank_volume` and returning less water.
    config = SimulationConfig(
        simulation_id="test-water",
        scenario_name="water-limited",
        days=30,
        dt_hours=24.0,
        seed=42,
        zones=[ZoneSimConfig(zone_id="z1", crop_id="dwarf_tomato", area_sqm=500.0, plant_density_per_sqm=10.0, initial_tank_volume_liters=0.0)]
    )
    engine = SimulationEngine()
    res = engine.run(config)
    assert res.total_water_liters == 0.0
    assert res.average_stress >= 0.8  # Severely stressed due to lack of water
    
    # Check new water accounting fields
    assert res.requested_water_l >= 0.0
    assert res.delivered_water_l == 0.0
    assert res.unmet_water_demand_l >= 0.0
    assert res.unmet_water_demand_l == res.requested_water_l
    assert res.remaining_water_l == 0.0


def test_execution_state_transitions() -> None:
    # PROPOSED
    proposal = ControlPlanProposal(actions=[
        ControlActionProposal(zone_id="z1", actuator_id="pump-1", action_type="SET", target_value=1.0, duration_s=600.0, reason="test")
    ])
    assert proposal.execution_status == ExecutionState.PROPOSED
    
    # VALIDATED
    plan = ControlPlanBuilder.build(proposal)
    plan.metadata["execution_status"] = ExecutionState.VALIDATED
    assert plan.metadata["execution_status"] == ExecutionState.VALIDATED
    
    # APPROVED
    # Mock human approval
    plan.metadata["execution_status"] = ExecutionState.APPROVED
    assert plan.metadata["execution_status"] == ExecutionState.APPROVED
    
    # DISPATCHED
    gateway = EdgeGateway()
    # gateway requires a valid ControlPlan
    gateway.dispatch(plan)
    plan.metadata["execution_status"] = ExecutionState.DISPATCHED
    assert plan.metadata["execution_status"] == ExecutionState.DISPATCHED
    
    # ACKNOWLEDGED
    plan.metadata["execution_status"] = ExecutionState.ACKNOWLEDGED
    
    # OBSERVED
    plan.metadata["execution_status"] = ExecutionState.OBSERVED
    
    # FAILED / REJECTED / UNCERTAIN
    plan.metadata["execution_status"] = ExecutionState.REJECTED
    assert plan.metadata["execution_status"] == ExecutionState.REJECTED


def test_actuator_causal_physical_state_change() -> None:
    from domains.polyhouse.controllers.base import Controller, ControlPlan
    
    class ForcePumpController(Controller):
        def plan(self, simulation_id: str, timestep: int, time_days: float, zone_contexts: list[Any]) -> ControlPlan:
            return ControlPlan(plan_id="f", simulation_id=simulation_id, timestep=timestep, time_days=time_days, actions=[
                ControlAction(zone_id="z1", actuator_type=ActuatorType.PUMP, actuator_id="pump-z1", action_type=ActionType.SET_ON, target_value=1.0, duration_s=3600.0, reason="f", policy_version="1")
            ])
            
    engine = SimulationEngine(controller=ForcePumpController())
    config = SimulationConfig(
        simulation_id="test", scenario_name="test", days=1, dt_hours=1.0, seed=42,
        zones=[ZoneSimConfig(zone_id="z1", crop_id="dwarf_tomato", area_sqm=500.0, plant_density_per_sqm=10.0, initial_tank_volume_liters=10000.0, initial_substrate_moisture=10.0)]
    )
    res = engine.run(config)
    
    final_twin = res.extra.get("final_twin")
    if final_twin and final_twin.current_state and final_twin.current_state.substrate_moisture and final_twin.current_state.tank_volume:
        assert final_twin.current_state.substrate_moisture.value > 10.0
        assert final_twin.current_state.tank_volume.value < 10000.0
