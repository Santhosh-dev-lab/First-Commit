from domains.polyhouse.controllers.base import (
    ActionType,
    ActuatorType,
    ControlAction,
    ControlPlan,
)
from domains.polyhouse.edge.gateway import EdgeGateway


def test_edge_gateway_dispatch() -> None:
    gateway = EdgeGateway()
    plan = ControlPlan(
        plan_id="plan-1",
        simulation_id="sim-1",
        timestep=0,
        time_days=0.0,
        actions=[
            ControlAction(
                zone_id="z1",
                actuator_type=ActuatorType.PUMP,
                actuator_id="pump-z1",
                action_type=ActionType.SET_ON,
                target_value=1.0,
                duration_s=1800.0,
                reason="test",
                policy_version="1.0"
            ),
            ControlAction(
                zone_id="z1",
                actuator_type=ActuatorType.VENT,
                actuator_id="vent-z1",
                action_type=ActionType.SET_VALUE,
                target_value=0.5,
                duration_s=3600.0,
                reason="test",
                policy_version="1.0"
            ),
            ControlAction(
                zone_id="z1",
                actuator_type=ActuatorType.FAN,
                actuator_id="fan-z1",
                action_type=ActionType.SET_OFF,
                target_value=0.0,
                duration_s=3600.0,
                reason="test",
                policy_version="1.0"
            ),
        ],
        metadata={},
    )

    commands = gateway.dispatch(plan)
    assert len(commands) == 3

    assert commands[0].protocol == "mqtt"
    assert commands[0].device_address == "broker_url"
    assert commands[0].register_or_topic == "polyhouse/z1/pump/set"
    assert commands[0].payload == 1

    assert commands[1].protocol == "mqtt"
    assert commands[1].device_address == "broker_url"
    assert commands[1].register_or_topic == "polyhouse/z1/vent/set"
    assert commands[1].payload == 0.5

    assert commands[2].protocol == "mqtt"
    assert commands[2].register_or_topic == "polyhouse/z1/fan/set"
    assert commands[2].payload == 0
