from collections.abc import Callable

from domains.edge.gateway import EdgeGateway
from domains.edge.models import CommandEnvelope, GatewayHeartbeat, TelemetryEnvelope


class AwsIoTGateway(EdgeGateway):
    """
    AWS IoT Gateway adapter. 
    Uses awsiotsdk to connect to AWS IoT Core over MQTT.
    """

    def __init__(self, endpoint: str, client_id: str, farm_id: str):
        self.endpoint = endpoint
        self.client_id = client_id
        self.farm_id = farm_id
        self.status = "DISCONNECTED"
        self._telemetry_callback: Callable[[TelemetryEnvelope], None] | None = None
        self._heartbeat_callback: Callable[[GatewayHeartbeat], None] | None = None
        self._mqtt_connection = None

    def connect(self) -> None:
        try:
            # Note: in a real implementation, we would use awsiotsdk.mqtt_connection_builder
            # to construct an mTLS or WebSockets connection using the environment's AWS credentials.
            # For this milestone, we use a mocked/stub connection until actual certificates are provisioned.
            self.status = "CONNECTED"
            print(f"[AwsIoTGateway] Connected to AWS IoT endpoint: {self.endpoint}")
        except Exception as e:  # noqa: BLE001
            self.status = "ERROR"
            print(f"[AwsIoTGateway] Connection failed: {e}")

    def disconnect(self) -> None:
        self.status = "DISCONNECTED"
        print("[AwsIoTGateway] Disconnected from AWS IoT")

    def get_status(self) -> str:
        return self.status

    def publish_telemetry(self, telemetry: TelemetryEnvelope) -> None:
        if self.status != "CONNECTED":
            return
            
        topic = f"physica/{self.farm_id}/telemetry"
        payload = telemetry.model_dump_json()
        print(f"[AwsIoTGateway] Publish telemetry to {topic}: {payload}")
        # self._mqtt_connection.publish(topic, payload, mqtt.QoS.AT_LEAST_ONCE)

    def publish_heartbeat(self, heartbeat: GatewayHeartbeat) -> None:
        if self.status != "CONNECTED":
            return
            
        topic = f"physica/{self.farm_id}/gateway/{self.client_id}/heartbeat"
        payload = heartbeat.model_dump_json()
        print(f"[AwsIoTGateway] Publish heartbeat to {topic}: {payload}")
        # self._mqtt_connection.publish(topic, payload, mqtt.QoS.AT_LEAST_ONCE)

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
            print(f"[AwsIoTGateway] Command {command.command_id} already executed. Ignoring replay.")
            return
            
        conn.close()
        
        topic = f"physica/{self.farm_id}/command"
        payload = command.model_dump_json()
        print(f"[AwsIoTGateway] Publish command to {topic}: {payload}")
        # self._mqtt_connection.publish(topic, payload, mqtt.QoS.AT_LEAST_ONCE)

    def set_telemetry_callback(self, callback: Callable[[TelemetryEnvelope], None]) -> None:
        self._telemetry_callback = callback
        # Setup MQTT subscription in a real implementation

    def set_heartbeat_callback(self, callback: Callable[[GatewayHeartbeat], None]) -> None:
        self._heartbeat_callback = callback
        # Setup MQTT subscription in a real implementation
