from typing import Any

from schemas.tools import ControlPlanProposal
from tools.authority import ToolAuthority, ToolCategory


@ToolAuthority.register("get_digital_twin_state", ToolCategory.READ_ONLY)
def get_digital_twin_state(zone_id: str) -> dict[str, Any]:
    """Retrieves the current physical state of the digital twin for a zone."""
    # This will be wired to the real twin later or injected.
    # For now, we define the tool signature.
    return {"zone": zone_id, "temperature": 22.0, "status": "nominal"}

@ToolAuthority.register("simulate_scenario", ToolCategory.COMPUTATIONAL)
def simulate_scenario(zone_id: str, water_quota: float) -> dict[str, Any]:
    """Runs a deterministic physics simulation for a given quota."""
    return {"predicted_stress": 0.1}

@ToolAuthority.register("create_control_plan_proposal", ToolCategory.PROPOSAL)
def create_control_plan_proposal(actions: list[dict[str, Any]]) -> ControlPlanProposal:
    """Proposes a series of actions. Returns a ControlPlanProposal."""
    # Simplified instantiation
    return ControlPlanProposal(actions=[])

@ToolAuthority.register("execute_pump", ToolCategory.EXECUTION)
def execute_pump(zone_id: str, state: bool) -> str:
    """Directly executes physical hardware. Restricted to Execution layer."""
    return f"Pump in {zone_id} turned {'ON' if state else 'OFF'}"
