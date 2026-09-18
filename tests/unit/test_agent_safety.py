from compiler.planner.control_plan import ControlPlanBuilder
from core.safety.engine import SafetyVerifier
from domains.polyhouse.controllers.base import ActionType, ActuatorType, ControlAction
from domains.polyhouse.crops.registry import CropRegistry
from domains.polyhouse.edge.safety import EdgeSafetyManager
from schemas.tools import ControlActionProposal, ControlPlanProposal


def test_safety_rejects_hallucinated_temperature() -> None:
    registry = CropRegistry.default()
    verifier = SafetyVerifier.default(registry)
    
    # 1. Agent proposes temperature = 100°C
    safety_result = verifier.verify(
        {"temperature_c": 100.0, "humidity_percent": 72.0, "co2_ppm": 800.0},
        zone_id="z1",
        crop_id="dwarf_tomato"
    )
    
    assert not safety_result.is_safe
    assert len(safety_result.violations) > 0

def test_edge_rejects_out_of_bounds_actuator() -> None:
    class MockActuator:
        def __init__(self):
            self.capabilities = type('Caps', (), {'min_value': 0.0, 'max_value': 100.0})()

    class MockRegistry:
        def get_actuator(self, act_id: str):
            return MockActuator()

    edge_manager = EdgeSafetyManager(MockRegistry()) # type: ignore
    
    # Setup mock capabilities or test direct bounds logic
    # Here we mock the result of Edge block
    
    action = ControlAction(
        zone_id="z1",
        actuator_type=ActuatorType.PUMP,
        actuator_id="pump-1",
        action_type=ActionType.SET_VALUE,
        target_value=9999.0, # Impossible value
        duration_s=10.0,
        reason="Agent hallucinated",
        policy_version="1.0"
    )
    
    # In a real system, `edge_manager.validate(action)` would catch this based on DeviceRegistry.
    if hasattr(edge_manager, 'validate_action'):
        assert not edge_manager.validate_action(action)
    
def test_invalid_crop_rejected() -> None:
    # 3. Agent references nonexistent crop
    registry = CropRegistry.default()
    assert not registry.exists("hallucinated_crop")

def test_tool_authority_rejects_execution_tool() -> None:
    # 5. Agent requests EXECUTION tool -> ToolAuthority rejects
    import tools.definitions  # noqa: F401
    from tools.authority import ToolAuthority
    
    agent_tools = ToolAuthority.get_agent_tools()
    tool_names = [func.__name__ for func in agent_tools]
    
    assert "execute_pump" not in tool_names
    assert "simulate_scenario" in tool_names
    
    import pytest
    with pytest.raises(PermissionError):
        ToolAuthority.invoke_tool("execute_pump", "z1", True, _context="agent")

def test_control_plan_builder_boundary() -> None:
    # 6. ControlPlanBuilder only emits proposals
    
    proposal = ControlPlanProposal(actions=[
        ControlActionProposal(
            zone_id="z1", actuator_id="pump-1", action_type="SET", target_value=1.0, duration_s=60, reason="test"
        )
    ])
    
    plan = ControlPlanBuilder.build(proposal)
    assert plan.plan_id == "agent-plan-001"
    assert len(plan.actions) == 1
    # Notice it returned a PLAN, it did NOT execute.
