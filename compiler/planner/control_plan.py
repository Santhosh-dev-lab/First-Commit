from domains.polyhouse.controllers.base import (
    ActionType,
    ActuatorType,
    ControlAction,
    ControlPlan,
)
from schemas.tools import ControlPlanProposal


class ControlPlanBuilder:
    """
    Deterministically converts a ControlPlanProposal into an executable ControlPlan.
    This acts as the semantic validation boundary.
    """
    
    @staticmethod
    def build(proposal: ControlPlanProposal) -> ControlPlan:
        # In a real implementation this would check devices from DeviceRegistry
        actions = []
        for p_action in proposal.actions:
            # Map action types and actuator types safely
            action_type_map = {
                "SET_ON": ActionType.SET_ON,
                "SET_OFF": ActionType.SET_OFF,
                "SET_VALUE": ActionType.SET_VALUE,
                "SET": ActionType.SET_VALUE,
            }
            actuator_type_map = {
                "PUMP": ActuatorType.PUMP,
                "VENT": ActuatorType.VENT,
                "HEATER": ActuatorType.HEATER,
                "LIGHT": ActuatorType.GROW_LIGHT,
            }
            
            a_type = action_type_map.get(p_action.action_type.upper(), ActionType.SET_VALUE)
            act_type = actuator_type_map.get(p_action.actuator_id.split("-")[0].upper(), ActuatorType.PUMP)
            
            actions.append(ControlAction(
                zone_id=p_action.zone_id,
                actuator_id=p_action.actuator_id,
                actuator_type=act_type,
                action_type=a_type,
                target_value=p_action.target_value,
                duration_s=p_action.duration_s,
                reason=p_action.reason,
                policy_version="agent-1.0",
            ))
            
        return ControlPlan(
            plan_id="agent-plan-001",
            simulation_id="agent-sim-001",
            timestep=0,
            time_days=0.0,
            actions=actions
        )
