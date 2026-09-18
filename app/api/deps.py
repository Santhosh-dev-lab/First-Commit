from typing import Any

from fastapi import Depends, HTTPException

from app.services.auth_service import UserInfo, get_current_user
from app.services.farm_service import FarmService


def get_authorized_farm(user: UserInfo = Depends(get_current_user)) -> dict[str, Any]:
    """
    Retrieves the farm for the authenticated user and asserts authorization.
    In a fully multi-tenant setup with many farms per user, this would accept 
    a farm_id parameter. For the current 1:1 architecture, it safely retrieves 
    the single owned farm and blocks access if not found.
    """
    farm_data = FarmService.get_user_farm(user.id)
    if not farm_data:
        raise HTTPException(status_code=404, detail="Farm not found or access denied")
    
    # Check role if needed (e.g. if we had cross-tenant operators)
    # Right now, get_user_farm enforces ownership via user_id
    
    return farm_data
