from __future__ import annotations

import dataclasses

from domains.polyhouse.controllers.base import (
    ActionType,
    ActuatorType,
    ControlAction,
    ZoneControlContext,
)
from domains.polyhouse.controllers.baseline import BaselineControlPolicy


class ReducedIrrigationPolicy(BaselineControlPolicy):
    """
    Operates with a negative offset to the target moisture.
    Saves water but increases the likelihood of crop stress.
    """
    def __init__(self, moisture_offset: float = -10.0, **kwargs):
        super().__init__(policy_id="reduced-irrigation", **kwargs)
        self._VERSION = "1.0.0"
        self.moisture_offset = moisture_offset

    def decide(self, context: ZoneControlContext) -> list[ControlAction]:
        # Override the target moisture percent
        original_target = context.target_moisture_percent
        context.target_moisture_percent = max(0.0, original_target + self.moisture_offset)
        actions = super().decide(context)
        # Restore just in case
        context.target_moisture_percent = original_target
        
        final_actions = []
        for a in actions:
            new_extra = dict(a.extra)
            new_extra["moisture_offset"] = self.moisture_offset
            final_actions.append(dataclasses.replace(
                a,
                policy_version=self.version,
                extra=new_extra
            ))
        return final_actions


class PulseIrrigationPolicy(BaselineControlPolicy):
    """
    Overrides the baseline pump duration to run frequent, smaller pulses.
    Helps prevent runoff and improves water efficiency.
    """
    def __init__(self, pulse_duration_s: float = 300.0, **kwargs):
        super().__init__(policy_id="pulse-irrigation", **kwargs)
        self._VERSION = "1.0.0"
        self.pulse_duration_s = pulse_duration_s

    def decide(self, context: ZoneControlContext) -> list[ControlAction]:
        actions = super().decide(context)
        final_actions = []
        for a in actions:
            new_reason = a.reason
            new_duration_s = a.duration_s
            if a.actuator_type == ActuatorType.PUMP and a.action_type == ActionType.SET_ON:
                new_duration_s = self.pulse_duration_s
                new_reason += f" (Pulse limit: {self.pulse_duration_s}s)"
            
            new_extra = dict(a.extra)
            new_extra["pulse_duration_s"] = self.pulse_duration_s
            final_actions.append(dataclasses.replace(
                a,
                duration_s=new_duration_s,
                reason=new_reason,
                policy_version=self.version,
                extra=new_extra
            ))
        return final_actions


class AdaptiveIrrigationPolicy(BaselineControlPolicy):
    """
    Only irrigates if stress index is near critical or moisture is very low.
    Adapts based on the crop stress rather than just target moisture.
    """
    def __init__(self, stress_threshold: float = 0.5, **kwargs):
        super().__init__(policy_id="adaptive-irrigation", **kwargs)
        self._VERSION = "1.0.0"
        self.stress_threshold = stress_threshold

    def decide(self, context: ZoneControlContext) -> list[ControlAction]:
        actions = super().decide(context)
        
        # Filter out PUMP_ON if stress is below threshold and moisture isn't critically low
        final_actions = []
        for a in actions:
            new_reason = a.reason
            if a.actuator_type == ActuatorType.PUMP and a.action_type == ActionType.SET_ON:
                critical_moisture = context.target_moisture_percent - 15.0
                if context.crop_stress_index < self.stress_threshold and context.substrate_moisture_percent > critical_moisture:
                    # Skip irrigation to save water
                    continue
                else:
                    new_reason = f"Stress ({context.crop_stress_index:.2f}) or critical moisture. Irrigating."
            
            new_extra = dict(a.extra)
            new_extra["stress_threshold"] = self.stress_threshold
            final_actions.append(dataclasses.replace(
                a,
                reason=new_reason,
                policy_version=self.version,
                extra=new_extra
            ))
            
        return final_actions
