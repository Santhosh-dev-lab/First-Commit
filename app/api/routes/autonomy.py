from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_authorized_farm, get_current_user
from app.services.auth_service import UserInfo
from app.services.receding_horizon import RecedingHorizonController, autonomy_repo
from schemas.autonomy import AutonomyRun, PlanningHorizon
from schemas.experiments import FarmObjective, ObjectiveWeights


class StartAutonomyRequest(BaseModel):
    objective: FarmObjective
    weights: ObjectiveWeights
    horizon: PlanningHorizon

router = APIRouter()
controller = RecedingHorizonController()

@router.post("/start", response_model=AutonomyRun)
def start_autonomy(
    request: StartAutonomyRequest,
    user: UserInfo = Depends(get_current_user),
    farm: dict[str, Any] = Depends(get_authorized_farm)
):
    return controller.start_run(
        farm_id=farm["farm"]["id"],
        objective=request.objective,
        weights=request.weights,
        planning_horizon=request.horizon
    )

@router.post("/step")
def step_autonomy(
    run_id: str,
    scenario: str = "WATER_SHORTAGE",
    user: UserInfo = Depends(get_current_user),
    farm: dict[str, Any] = Depends(get_authorized_farm)
):
    run = autonomy_repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    if run.farm_id != farm["farm"]["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized for this run")
        
    cycle = controller.step_run(run_id=run_id, user_id=user.id, scenario=scenario)
    return {"status": "SUCCESS", "cycle": cycle}

@router.get("/{run_id}", response_model=AutonomyRun)
def get_autonomy_run(
    run_id: str,
    user: UserInfo = Depends(get_current_user),
    farm: dict[str, Any] = Depends(get_authorized_farm)
):
    run = autonomy_repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    if run.farm_id != farm["farm"]["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized for this run")
        
    return run

@router.get("/{run_id}/cycles")
def get_autonomy_cycles(
    run_id: str,
    user: UserInfo = Depends(get_current_user),
    farm: dict[str, Any] = Depends(get_authorized_farm)
):
    run = autonomy_repo.get_run(run_id)
    if not run or run.farm_id != farm["farm"]["id"]:
        raise HTTPException(status_code=404, detail="Run not found")
        
    return autonomy_repo.get_cycles(run_id)
