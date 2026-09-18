from typing import Any

from domains.polyhouse.controllers.base import ControlPolicy
from domains.polyhouse.controllers.baseline import BaselineControlPolicy
from domains.polyhouse.controllers.strategies import (
    AdaptiveIrrigationPolicy,
    PulseIrrigationPolicy,
    ReducedIrrigationPolicy,
)


def get_policy(policy_id: str, parameters: dict[str, Any] | None = None) -> ControlPolicy:
    """
    Factory to map a policy_id to its ControlPolicy instance.
    """
    params = parameters or {}
    
    if policy_id == "BASELINE":
        return BaselineControlPolicy(**params)
    elif policy_id == "REDUCED_IRRIGATION":
        return ReducedIrrigationPolicy(**params)
    elif policy_id == "PULSE_IRRIGATION":
        return PulseIrrigationPolicy(**params)
    elif policy_id == "ADAPTIVE_IRRIGATION":
        return AdaptiveIrrigationPolicy(**params)
    else:
        raise ValueError(f"Unknown policy_id: {policy_id}")
