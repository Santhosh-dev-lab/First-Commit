"""
domains/polyhouse/edge/gateway.py

Edge Gateway Layer for PHYSICA.
Responsible for translating high-level ControlPlan actions into
hardware-specific protocol messages (e.g., Modbus, MQTT).

This layer isolates the physical actuation protocols from the
control algorithms.
"""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel

from domains.polyhouse.controllers.base import (
    ActionType,
    ControlPlan,
)


class EdgeCommand(BaseModel):
    """A low-level hardware command generated from a ControlAction."""
    protocol: str
    device_address: str
    register_or_topic: str
    payload: Any
    timestamp: float


from domains.polyhouse.devices.registry import DeviceRegistry

from .safety import EdgeSafetyManager


class EdgeGateway:
    """
    Translates semantic ControlPlan actions into EdgeCommand payloads.
    """

    def __init__(self, device_registry: DeviceRegistry | None = None) -> None:
        self.device_registry = device_registry
        self.safety_manager = EdgeSafetyManager(device_registry) if device_registry else None

    def dispatch(self, plan: ControlPlan, offline: bool = False) -> list[EdgeCommand]:
        """
        Convert a ControlPlan into executable EdgeCommands.
        """
        from schemas.tools import ExecutionState
        if not isinstance(plan, ControlPlan):
            raise TypeError("EdgeGateway strictly requires a validated ControlPlan. ControlPlanProposal is rejected.")
            
        commands: list[EdgeCommand] = []
        now = time.time()
        
        # Local Safety validation
        valid_actions = plan.actions
        if self.safety_manager:
            valid_actions = self.safety_manager.validate_plan(plan)

        for action in valid_actions:
            # Fallback for simplicity if device_registry is missing
            protocol = "mqtt"
            address = "broker_url"
            register = f"polyhouse/{action.zone_id}/{action.actuator_type.value.lower()}/set"
            
            if self.device_registry:
                actuator = self.device_registry.get_actuator(action.actuator_id)
                if not actuator:
                    continue # Unknown device
            
            # Map the value
            payload: Any = 0
            if action.action_type == ActionType.SET_ON:
                payload = 1
            elif action.action_type == ActionType.SET_OFF:
                payload = 0
            elif action.action_type == ActionType.SET_VALUE:
                payload = round(action.target_value, 2)

            cmd = EdgeCommand(
                protocol=protocol,
                device_address=address,
                register_or_topic=register,
                payload=payload,
                timestamp=now,
            )
            commands.append(cmd)

        if hasattr(plan, 'metadata'):
            plan.metadata["execution_status"] = ExecutionState.DISPATCHED.value
            
        return commands
