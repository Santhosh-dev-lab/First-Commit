from fastapi import APIRouter
from app.api.schemas import ResourceResponse, TelemetryResponse
from app.services.physica_service import physica_service

router = APIRouter()

@router.get("/resources", response_model=ResourceResponse)
def get_resources() -> ResourceResponse:
    return physica_service.get_resources()

@router.get("/telemetry", response_model=list[TelemetryResponse])
def get_telemetry() -> list[TelemetryResponse]:
    return physica_service.get_telemetry()
