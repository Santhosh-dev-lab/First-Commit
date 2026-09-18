import time

from app.services.repositories import execution_repo, plan_repo
from domains.edge.models import TelemetryEnvelope
from schemas.tools import ExecutionState


class ReconciliationService:
    def observe(self, telemetry: TelemetryEnvelope) -> None:
        """
        Observes incoming telemetry and reconciles it against pending ACKNOWLEDGED commands
        to confirm their physical effect.
        """
        # Find all executions that are ACKNOWLEDGED but not OBSERVED
        # (For efficiency, in a real system this would use an indexed query. Here we iterate).
        all_executions = execution_repo.get_all()
        for exec_id in all_executions:
            record = execution_repo.get(exec_id)
            if not record or record.get("status") != "ACKNOWLEDGED":
                continue
                
            if record.get("farm_id") != telemetry.farm_id:
                continue
                
            # We need to verify if this telemetry confirms the command's effect
            plan_id = record.get("plan_id")
            plan = plan_repo.get(plan_id)
            if not plan:
                continue
                
            # Verify temporal validity: telemetry must be generated AFTER the command was acknowledged
            ack_time = record.get("acknowledged_at", 0)
            if telemetry.timestamp < ack_time:
                continue
                
            # Check if this telemetry matches the zone of the actions
            # A ControlPlanProposal can have multiple actions. For simplicity, we check if ALL actions are observed.
            # Here we just look at the first action as they usually apply to one zone.
            all_observed = True
            for action in plan.actions:
                if action.zone_id != telemetry.zone_id:
                    all_observed = False
                    break
                    
                # We expect the telemetry to reflect the physical state change.
                # For instance, if action was PUMP_ON to reduce water stress, moisture should increase or stress decrease.
                # Alternatively, the virtual actuator's state is reported in telemetry.
                # Let's verify the physical effect based on the action type.
                effect_confirmed = False
                if action.action_type in ("SET_ON", "SET_VALUE", "PUMP_ON") and "pump" in action.actuator_id.lower():
                    # For a pump, we expect moisture to be > 60% or stress to decrease
                    moisture = telemetry.measurements.get("substrate_moisture", telemetry.measurements.get("moisture", 0.0))
                    # If pump was turned on, and moisture is high enough or rising, we consider it observed.
                    # Or we just check if it's > 70
                    if moisture > 70.0:
                        effect_confirmed = True
                else:
                    # Generic fallback: if telemetry comes from the same zone after ACK, consider it observed.
                    # (In a real system, we'd have precise physics thresholds)
                    effect_confirmed = True
                    
                if not effect_confirmed:
                    all_observed = False
                    break
                    
            if all_observed:
                record["status"] = "OBSERVED"
                record["observed_at"] = time.time()
                execution_repo.save(exec_id, record)
                
                plan.execution_status = ExecutionState.OBSERVED
                plan_repo.save(plan_id, plan)

reconciliation_service = ReconciliationService()
