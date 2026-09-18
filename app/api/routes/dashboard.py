from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_authorized_farm
from app.api.schemas import DashboardSnapshot
from app.services.physica_service import PhysicaApplicationService

router = APIRouter(tags=["dashboard"])

physica_service = PhysicaApplicationService()

@router.get("/dashboard", response_model=DashboardSnapshot)
def get_dashboard_snapshot(farm_data: dict[str, Any] = Depends(get_authorized_farm)) -> DashboardSnapshot:
    """Returns the unified dashboard state for the authorized farm."""
    return physica_service.get_dashboard_snapshot(farm_data["farm"]["id"])
