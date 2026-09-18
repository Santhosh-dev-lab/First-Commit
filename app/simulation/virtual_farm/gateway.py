import sqlite3
import time
import uuid
from collections.abc import Callable

from app.db.database import get_db
from app.services.telemetry_ingestion import telemetry_ingestion_service
from domains.edge.gateway import EdgeGateway
from domains.edge.models import CommandEnvelope, GatewayHeartbeat, TelemetryEnvelope


class VirtualEdgeGateway(EdgeGateway):
    def __init__(self, farm_id: str, client_id: str = "virtual-gateway"):
        self.farm_id = farm_id
        self.client_id = client_id
        self.status = "DISCONNECTED"
        self._telemetry_callback: Callable[[TelemetryEnvelope], None] | None = None
        self._heartbeat_callback: Callable[[GatewayHeartbeat], None] | None = None
        self._command_queue: list[CommandEnvelope] = []

    def connect(self) -> None:
        self.status = "CONNECTED"

    def disconnect(self) -> None:
        self.status = "DISCONNECTED"

    def get_status(self) -> str:
        return self.status

    def publish_telemetry(self, telemetry: TelemetryEnvelope) -> None:
        if self.status != "CONNECTED":
            return
            
        # In a real environment, this goes over MQTT, then is picked up by a service that calls TelemetryIngestionService.
        # Here we bridge it directly as required.
        telemetry_ingestion_service.process_telemetry(telemetry)
        
        if self._telemetry_callback:
            self._telemetry_callback(telemetry)

    def publish_heartbeat(self, heartbeat: GatewayHeartbeat) -> None:
        if self.status != "CONNECTED":
            return
        if self._heartbeat_callback:
            self._heartbeat_callback(heartbeat)

    def send_command(self, command: CommandEnvelope) -> None:
        if self.status != "CONNECTED":
            return
            
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO command_execution_log (id, command_id, farm_id, executed_at) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), command.command_id, self.farm_id, time.time())
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            # Duplicate command, ignore
            return
            
        conn.close()
        
        # Parse execution_id and mark ACKNOWLEDGED
        parts = command.command_id.split('_')
        if len(parts) >= 3 and parts[0] == "cmd":
            execution_id = parts[1]
            from app.services.repositories import execution_repo, plan_repo
            from schemas.tools import ExecutionState
            record = execution_repo.get(execution_id)
            if record:
                record["status"] = "ACKNOWLEDGED"
                record["acknowledged_at"] = time.time()
                execution_repo.save(execution_id, record)
                
                plan = plan_repo.get(record["plan_id"])
                if plan and plan.execution_status != ExecutionState.OBSERVED:
                    plan.execution_status = ExecutionState.ACKNOWLEDGED
                    plan_repo.save(record["plan_id"], plan)
        
        # Queue command for the VirtualFarmRuntime to process in the next tick
        self._command_queue.append(command)

    def set_telemetry_callback(self, callback: Callable[[TelemetryEnvelope], None]) -> None:
        self._telemetry_callback = callback

    def set_heartbeat_callback(self, callback: Callable[[GatewayHeartbeat], None]) -> None:
        self._heartbeat_callback = callback
        
    def get_pending_commands(self) -> list[CommandEnvelope]:
        cmds = self._command_queue.copy()
        self._command_queue.clear()
        return cmds
