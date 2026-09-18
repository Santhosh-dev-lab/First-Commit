import json
import time

from app.db.database import get_db
from app.services.farm_service import FarmService
from app.services.reconciliation import reconciliation_service
from app.services.telemetry_repository import telemetry_repo
from domains.edge.models import TelemetryEnvelope


class TelemetryIngestionService:
    def process_telemetry(self, envelope: TelemetryEnvelope) -> str:
        """
        Validates and ingests physical or simulated telemetry into the system.
        Returns the persistent record ID.
        """
        # 1. Validate Farm exists
        farm_data = FarmService.get_farm_by_id(envelope.farm_id)
        if not farm_data:
            raise ValueError(f"Farm {envelope.farm_id} does not exist.")

        # 2. Validate gateway belongs to farm
        # (Assuming farm_data has connections or we can query devices)
        # We will do a simple check for now: Devices must belong to the farm
        device_valid = False
        for dev in farm_data.get("devices", []):
            if dev["id"] == envelope.device_id:
                device_valid = True
                break
                
        # In Local simulation, devices might be dynamically simulated (e.g. "sim_sensor_zone1").
        # We allow it if the source is LOCAL_SIMULATION for now, or if it strictly matches a device.
        if not device_valid and envelope.source.value != "LOCAL_SIMULATION":
            raise ValueError(f"Device {envelope.device_id} not registered to Farm {envelope.farm_id}")

        # 3. Validate timestamp freshness
        now = time.time()
        age = now - envelope.timestamp
        if age > 86400: # Reject data older than 24h
            raise ValueError("Telemetry is too stale (>24h).")

        # 4. Validate sequence number for replay protection
        # If sequence numbers are provided, they must strictly increase.
        # If they aren't provided (e.g. legacy/mock device), we fallback to timestamp-only
        conn = get_db()
        cursor = conn.cursor()
        
        # We try to get the latest sequence number for this device
        cursor.execute("SELECT measurements FROM telemetry_records WHERE device_id=? ORDER BY timestamp DESC LIMIT 1", (envelope.device_id,))
        row = cursor.fetchone()
        if row:
            try:
                meas = json.loads(row['measurements'])
                last_seq = meas.get("_sequence_number")
                current_seq = envelope.measurements.get("_sequence_number")
                
                if last_seq is not None and current_seq is not None and current_seq <= last_seq:
                    conn.close()
                    raise ValueError(f"Telemetry replay detected for device {envelope.device_id} (seq {current_seq} <= {last_seq})")
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
                
        conn.close()

        # 5. Save to Repository
        record_id = telemetry_repo.save(envelope)
        
        # 6. Reconcile pending commands
        reconciliation_service.observe(envelope)
        
        return record_id

telemetry_ingestion_service = TelemetryIngestionService()
