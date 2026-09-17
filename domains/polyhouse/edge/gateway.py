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

from domains.polyhouse.controllers.base import ActionType, ActuatorType, ControlAction, ControlPlan


class EdgeCommand(BaseModel):
    """A low-level hardware command generated from a ControlAction."""
    protocol: str
    device_address: str
    register_or_topic: str
    payload: Any
    timestamp: float


class EdgeGateway:
    """
    Translates semantic ControlPlan actions into EdgeCommand payloads.
    """

    def __init__(self, hardware_map: dict[str, dict[str, Any]] | None = None) -> None:
        # Default mock hardware map mapping actuator_id to Modbus/MQTT configs
        self.hardware_map = hardware_map or {
            "pump-z1": {"protocol": "modbus", "address": "0x01", "register": "40001"},
            "vent-z1": {"protocol": "modbus", "address": "0x02", "register": "40002"},
            "fan-z1":  {"protocol": "mqtt", "topic": "polyhouse/z1/fan/set"},
            "heater-z1": {"protocol": "mqtt", "topic": "polyhouse/z1/heater/set"},
            "fogger-z1": {"protocol": "modbus", "address": "0x03", "register": "40003"},
        }

    def dispatch(self, plan: ControlPlan) -> list[EdgeCommand]:
        """
        Convert a ControlPlan into executable EdgeCommands.
        """
        commands: list[EdgeCommand] = []
        now = time.time()

        for action in plan.actions:
            hw_config = self.hardware_map.get(action.actuator_id)
            if not hw_config:
                # Fallback to generic MQTT topic if not mapped
                hw_config = {
                    "protocol": "mqtt",
                    "topic": f"polyhouse/fallback/{action.zone_id}/{action.actuator_type.value}/set",
                }

            # Map the value
            payload: Any = 0
            if action.action_type == ActionType.SET_ON:
                payload = 1
            elif action.action_type == ActionType.SET_OFF:
                payload = 0
            elif action.action_type == ActionType.SET_VALUE:
                # Modbus might expect 0-10000 (0-100.00%)
                if hw_config["protocol"] == "modbus":
                    payload = int(action.target_value * 10000)
                else:
                    payload = round(action.target_value, 2)

            if hw_config["protocol"] == "modbus":
                cmd = EdgeCommand(
                    protocol="modbus",
                    device_address=hw_config["address"],
                    register_or_topic=hw_config["register"],
                    payload=payload,
                    timestamp=now,
                )
            else:
                cmd = EdgeCommand(
                    protocol="mqtt",
                    device_address="broker_url",
                    register_or_topic=hw_config["topic"],
                    payload=payload,
                    timestamp=now,
                )
            commands.append(cmd)

        return commands
