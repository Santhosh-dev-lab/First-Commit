from typing import Any

from fastapi import APIRouter

from app.api.schemas import TwinResponse
from app.services.physica_service import physica_service

router = APIRouter()

@router.get("/twin", response_model=TwinResponse)
def get_twin() -> TwinResponse:
    return physica_service.get_twin_state()

@router.get("/zones")
def get_zones() -> list[Any]:
    return physica_service.get_twin_state().zones

@router.get("/crops")
def get_crops() -> list[dict[str, str]]:
    # In a real implementation this would query the crop registry
    # For now, return mock crop data to unblock dashboard development
    return [{"crop_id": "dwarf_tomato", "name": "Dwarf Tomato"}, {"crop_id": "lettuce", "name": "Lettuce"}]
