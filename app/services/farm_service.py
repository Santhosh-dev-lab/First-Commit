import json
from typing import Any

from app.db.database import get_db


class FarmService:
    @staticmethod
    def get_user_farm(user_id: str) -> dict[str, Any] | None:
        """Returns the single farm for the user, or None if not found."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM farms WHERE user_id = ?", (user_id,))
        farm = cursor.fetchone()
        
        if not farm:
            conn.close()
            return None
            
        farm_dict = dict(farm)
        
        # Load associated zones
        cursor.execute("SELECT * FROM zones WHERE farm_id = ?", (farm['id'],))
        zones = [dict(z) for z in cursor.fetchall()]
        
        # Load resources
        cursor.execute("SELECT * FROM resources WHERE farm_id = ?", (farm['id'],))
        resources = cursor.fetchone()
        
        # Load connections
        cursor.execute("SELECT * FROM farm_connections WHERE farm_id = ?", (farm['id'],))
        connection = cursor.fetchone()
        
        # Load devices
        cursor.execute("SELECT * FROM devices WHERE farm_id = ?", (farm['id'],))
        devices = [dict(d) for d in cursor.fetchall()]
        
        conn.close()
        
        return {
            "farm": farm_dict,
            "zones": zones,
            "resources": dict(resources) if resources else None,
            "connection": dict(connection) if connection else None,
            "devices": devices
        }

    @staticmethod
    def get_farm_by_id(farm_id: str) -> dict[str, Any] | None:
        """Returns the farm data by farm_id, or None if not found."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM farms WHERE id = ?", (farm_id,))
        farm = cursor.fetchone()
        
        if not farm:
            conn.close()
            return None
            
        farm_dict = dict(farm)
        
        # Load associated zones
        cursor.execute("SELECT * FROM zones WHERE farm_id = ?", (farm_id,))
        zones = [dict(z) for z in cursor.fetchall()]
        
        # Load resources
        cursor.execute("SELECT * FROM resources WHERE farm_id = ?", (farm_id,))
        resources = cursor.fetchone()
        
        # Load connections
        cursor.execute("SELECT * FROM farm_connections WHERE farm_id = ?", (farm_id,))
        connection = cursor.fetchone()
        
        # Load devices
        cursor.execute("SELECT * FROM devices WHERE farm_id = ?", (farm_id,))
        devices = [dict(d) for d in cursor.fetchall()]
        
        conn.close()
        
        return {
            "farm": farm_dict,
            "zones": zones,
            "resources": dict(resources) if resources else None,
            "connection": dict(connection) if connection else None,
            "devices": devices
        }
        
    @staticmethod
    def get_latest_telemetry(farm_id: str, limit: int = 100) -> list[dict[str, Any]]:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telemetry_records WHERE farm_id = ? ORDER BY timestamp ASC LIMIT ?", (farm_id, limit))
        records = [dict(r) for r in cursor.fetchall()]
        
        # Parse JSON measurements
        for r in records:
            if isinstance(r['measurements'], str):
                try:
                    r['measurements'] = json.loads(r['measurements'])
                except (json.JSONDecodeError, TypeError):
                    r['measurements'] = {}
        
        conn.close()
        return records
