from collections.abc import Callable

from domains.edge.gateway import EdgeGateway
from domains.edge.models import CommandEnvelope, GatewayHeartbeat, TelemetryEnvelope


class LocalEdgeGateway(EdgeGateway):
    """
    Local Edge Gateway simulates a physical gateway's interface without real hardware or MQTT.
    It buffers telemetry and commands, triggering registered callbacks locally.
    """

    def __init__(self, gateway_id: str, farm_id: str):
        self.gateway_id = gateway_id
        self.farm_id = farm_id
        self.status = "DISCONNECTED"
        self._telemetry_callback: Callable[[TelemetryEnvelope], None] | None = None
        self._heartbeat_callback: Callable[[GatewayHeartbeat], None] | None = None

    def connect(self) -> None:
        self.status = "CONNECTED"

    def disconnect(self) -> None:
        self.status = "DISCONNECTED"

    def get_status(self) -> str:
        return self.status

    def publish_telemetry(self, telemetry: TelemetryEnvelope) -> None:
        if self.status != "CONNECTED":
            # Simulate offline buffering behavior by dropping it (for simple v1)
            return
            
        if self._telemetry_callback:
            self._telemetry_callback(telemetry)

    def publish_heartbeat(self, heartbeat: GatewayHeartbeat) -> None:
        if self.status != "CONNECTED":
            return
            
        if self._heartbeat_callback:
            self._heartbeat_callback(heartbeat)

    def send_command(self, command: CommandEnvelope) -> None:
        import sqlite3
        import time
        import uuid

        from app.db.database import get_db
        
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
            print(f"[LocalGateway] Command {command.command_id} already executed. Ignoring replay.")
            return
            
        conn.close()
        
        print(f"[LocalGateway] Received command: {command}")
        # In a real local setup, this might communicate over a serial port, Modbus, or direct GPIO.
        # For simulation, the backend simulator directly reads the actuator state or we simulate success.

    def set_telemetry_callback(self, callback: Callable[[TelemetryEnvelope], None]) -> None:
        self._telemetry_callback = callback

    def set_heartbeat_callback(self, callback: Callable[[GatewayHeartbeat], None]) -> None:
        self._heartbeat_callback = callback
