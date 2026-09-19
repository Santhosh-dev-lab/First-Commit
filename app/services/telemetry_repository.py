import json
import uuid
from typing import Any

from app.db.database import get_db
from domains.edge.models import TelemetryEnvelope


class TelemetryRepository:
    def save(self, envelope: TelemetryEnvelope) -> str:
        conn = get_db()
        cursor = conn.cursor()
        record_id = str(uuid.uuid4())
        
        cursor.execute(
            """
            INSERT INTO telemetry_records (id, farm_id, device_id, zone_id, timestamp, measurements, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                envelope.farm_id,
                envelope.device_id,
                envelope.zone_id,
                envelope.timestamp,
                json.dumps(envelope.measurements),
                envelope.source.value,
            )
        )
        conn.commit()
        conn.close()
        return record_id

    def get_latest_for_device(self, farm_id: str, device_id: str) -> dict[str, Any] | None:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM telemetry_records 
            WHERE farm_id = ? AND device_id = ? 
            ORDER BY timestamp DESC LIMIT 1
            """, 
            (farm_id, device_id)
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return dict(row)

    def get_latest_for_zone(self, farm_id: str, zone_id: str) -> dict[str, Any] | None:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM telemetry_records 
            WHERE farm_id = ? AND zone_id = ? 
            ORDER BY timestamp DESC LIMIT 1
            """, 
            (farm_id, zone_id)
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return dict(row)

telemetry_repo = TelemetryRepository()
