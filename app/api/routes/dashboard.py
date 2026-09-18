from fastapi import APIRouter, Depends
from app.api.schemas import DashboardSnapshot
from app.services.auth_service import UserInfo, get_current_user
from app.services.physica_service import physica_service

router = APIRouter()

@router.get("/dashboard", response_model=DashboardSnapshot)
def get_dashboard_snapshot(user: UserInfo = Depends(get_current_user)) -> DashboardSnapshot:
    """Fetch a unified snapshot of the dashboard data."""
    return physica_service.get_dashboard_snapshot(user.id)
