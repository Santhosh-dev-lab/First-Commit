from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.auth_service import UserInfo, get_current_user
from app.services.onboarding_service import (
    DeviceConfig,
    EnvironmentConfig,
    FarmConfig,
    FarmConnectionConfig,
    OnboardingService,
    OnboardingStatus,
    ResourceConfig,
    ZoneConfig,
)

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

class UpdateStepRequest(BaseModel):
    step: int

@router.get("/status")
def get_status(user: UserInfo = Depends(get_current_user)) -> OnboardingStatus:
    return OnboardingService.get_status(user.id)

@router.post("/step")
def update_step(req: UpdateStepRequest, user: UserInfo = Depends(get_current_user)):
    OnboardingService.update_step(user.id, req.step)
    return {"status": "success"}

@router.post("/farm")
def save_farm(req: FarmConfig, user: UserInfo = Depends(get_current_user)):
    farm_id = OnboardingService.save_farm(user.id, req)
    OnboardingService.update_step(user.id, 2)
    return {"status": "success", "farm_id": farm_id}

@router.post("/environment")
def save_environment(req: EnvironmentConfig, user: UserInfo = Depends(get_current_user)):
    env_id = OnboardingService.save_environment(user.id, req)
    OnboardingService.update_step(user.id, 3)
    return {"status": "success", "environment_id": env_id}

@router.post("/zones")
def save_zones(req: list[ZoneConfig], user: UserInfo = Depends(get_current_user)):
    OnboardingService.save_zones(user.id, req)
    OnboardingService.update_step(user.id, 4)
    return {"status": "success"}

@router.post("/resources")
def save_resources(req: ResourceConfig, user: UserInfo = Depends(get_current_user)):
    OnboardingService.save_resources(user.id, req)
    OnboardingService.update_step(user.id, 5)
    return {"status": "success"}

@router.post("/devices")
def save_devices(req: list[DeviceConfig], user: UserInfo = Depends(get_current_user)):
    OnboardingService.save_devices(user.id, req)
    OnboardingService.update_step(user.id, 6)
    return {"status": "success"}

@router.post("/connection")
def save_connection(req: FarmConnectionConfig, user: UserInfo = Depends(get_current_user)):
    OnboardingService.save_connection(user.id, req)
    OnboardingService.update_step(user.id, 7)
    return {"status": "success"}

@router.post("/complete")
def complete_onboarding(user: UserInfo = Depends(get_current_user)):
    OnboardingService.complete_onboarding(user.id)
    return {"status": "success"}
