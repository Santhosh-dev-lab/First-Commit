from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_authorized_farm, get_current_user
from app.services.auth_service import UserInfo
from app.services.experiment_service import ExperimentService, experiment_repo
from schemas.experiments import FarmObjective, ObjectiveWeights

router = APIRouter()

class ExperimentRunRequest(BaseModel):
    objective: FarmObjective
    weights: ObjectiveWeights
    scenario: str = Field(min_length=1, max_length=100)
    seed: int = 42
    days: int = 7

@router.post("")
def run_experiment(
    request: ExperimentRunRequest,
    farm: dict = Depends(get_authorized_farm)
) -> dict[str, Any]:
    farm_id = farm["farm"]["id"]
    service = ExperimentService()
    
    experiment = service.run_experiment(
        farm_id=farm_id,
        objective=request.objective,
        weights=request.weights,
        scenario=request.scenario,
        seed=request.seed,
        days=request.days
    )
    
    return experiment.model_dump()

@router.get("/{experiment_id}")
def get_experiment(
    experiment_id: str,
    farm: dict = Depends(get_authorized_farm)
) -> dict[str, Any]:
    experiment = experiment_repo.get(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    if experiment.farm_id != farm["farm"]["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized farm_id")
        
    return experiment.model_dump()

@router.get("/{experiment_id}/candidates")
def get_experiment_candidates(
    experiment_id: str,
    farm: dict = Depends(get_authorized_farm)
) -> dict[str, Any]:
    experiment = experiment_repo.get(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    if experiment.farm_id != farm["farm"]["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized farm_id")
        
    return {"candidates": [c.model_dump() for c in experiment.candidates]}

@router.get("/{experiment_id}/results")
def get_experiment_results(
    experiment_id: str,
    farm: dict = Depends(get_authorized_farm)
) -> dict[str, Any]:
    # Returns just the results for easier rendering
    experiment = experiment_repo.get(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    if experiment.farm_id != farm["farm"]["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized farm_id")
        
    return {
        "baseline": experiment.baseline.model_dump() if experiment.baseline else None,
        "selected_candidate_id": experiment.selected_candidate_id,
        "candidates": [c.model_dump() for c in experiment.candidates]
    }

@router.post("/{experiment_id}/execute")
def execute_experiment(
    experiment_id: str,
    user: UserInfo = Depends(get_current_user),
    farm: dict = Depends(get_authorized_farm)
) -> dict[str, Any]:
    farm_id = farm["farm"]["id"]
    service = ExperimentService()
    
    try:
        result = service.execute_selected_strategy(
            experiment_id=experiment_id,
            farm_id=farm_id,
            user_id=user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
