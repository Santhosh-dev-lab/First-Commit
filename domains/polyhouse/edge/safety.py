"""
domains/polyhouse/edge/safety.py

EdgeSafetyManager for offline and safety-critical edge validation.
"""


from domains.polyhouse.controllers.base import ControlAction, ControlPlan
from domains.polyhouse.devices.registry import DeviceRegistry
from twin.core import PolyhouseTwin


class EdgeSafetyManager:
    def __init__(self, device_registry: DeviceRegistry):
        self.device_registry = device_registry
        
    def validate_plan(self, plan: ControlPlan, twin: PolyhouseTwin | None = None) -> list[ControlAction]:
        """
        Validates a ControlPlan locally before execution.
        Returns the list of approved ControlActions.
        Rejected actions are logged/handled (for now we just drop them).
        """
        approved_actions = []
        for action in plan.actions:
            if self.validate_action(action, twin):
                approved_actions.append(action)
        return approved_actions

    def validate_action(self, action: ControlAction, twin: PolyhouseTwin | None = None) -> bool:
        """
        Validates a single ControlAction against the device's limits.
        """
        actuator = self.device_registry.get_actuator(action.actuator_id)
        if not actuator:
            # Reject if we don't know the actuator
            return False
            
        # In a real system, we'd also check twin state to ensure we don't open vents in a hurricane
        # or run pumps when there is a leak detected.
        return not (action.target_value < actuator.capabilities.min_value or action.target_value > actuator.capabilities.max_value)
