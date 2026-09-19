import time

import pytest
from pydantic import ValidationError

from app.services.telemetry_ingestion import telemetry_ingestion_service
from domains.edge.models import CommandEnvelope, TelemetryEnvelope, TelemetrySource


def test_telemetry_envelope_validation():
    # Valid envelope
    env = TelemetryEnvelope(
        farm_id="farm-123",
        gateway_id="gw-456",
        device_id="dev-789",
        timestamp=time.time(),
        source=TelemetrySource.EDGE_GATEWAY,
        measurements={"temperature_c": 24.5}
    )
    assert env.schema_version == "1.0"
    assert env.measurements["temperature_c"] == 24.5

    # Missing required field
    with pytest.raises(ValidationError):
        TelemetryEnvelope(
            farm_id="farm-123",
            device_id="dev-789",
            timestamp=time.time(),
            source=TelemetrySource.EDGE_GATEWAY,
            measurements={}
        )

def test_command_envelope_validation():
    cmd = CommandEnvelope(
        command_id="cmd-1",
        farm_id="f-1",
        gateway_id="gw-1",
        device_id="dev-1",
        timestamp=time.time(),
        command_type="PUMP_ON",
        parameters={"duration_s": 60}
    )
    assert cmd.command_type == "PUMP_ON"

def test_ingestion_rejects_stale_data():
    stale_time = time.time() - 90000 # 25 hours ago

    env = TelemetryEnvelope(
        farm_id="farm-test",
        gateway_id="gw-test",
        device_id="dev-test",
        timestamp=stale_time,
        source=TelemetrySource.EDGE_GATEWAY,
        measurements={"temp": 20.0}
    )

    with pytest.raises(ValueError, match="too stale"):
        from unittest.mock import patch
        with patch('app.services.farm_service.FarmService.get_farm_by_id') as mock_get_farm:
            mock_get_farm.return_value = {"id": "farm-test", "devices": [{"id": "dev-test"}]}
            telemetry_ingestion_service.process_telemetry(env)

def test_farm_isolation():
    env = TelemetryEnvelope(
        farm_id="farm-fake",
        gateway_id="gw-test",
        device_id="dev-test",
        timestamp=time.time(),
        source=TelemetrySource.EDGE_GATEWAY,
        measurements={}
    )
    
    with pytest.raises(ValueError, match="does not exist"):
        telemetry_ingestion_service.process_telemetry(env)
