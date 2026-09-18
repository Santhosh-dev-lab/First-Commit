import json
import time
import uuid
from typing import Any

from app.db.database import get_db


class AuditLogger:
    @staticmethod
    def log(event_type: str, result: str, user_id: str | None = None, farm_id: str | None = None, resource_id: str | None = None, request_id: str | None = None, metadata: dict[str, Any] | None = None) -> None:
        conn = get_db()
        cursor = conn.cursor()
        
        log_id = str(uuid.uuid4())
        now = time.time()
        
        meta_str = json.dumps(metadata) if metadata else None
        
        cursor.execute(
            "INSERT INTO audit_logs (id, timestamp, event_type, user_id, farm_id, resource_id, request_id, result, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (log_id, now, event_type, user_id, farm_id, resource_id, request_id, result, meta_str)
        )
        conn.commit()
        conn.close()

audit_logger = AuditLogger()
