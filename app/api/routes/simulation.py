from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_authorized_farm
from app.api.schemas import (
    SimulationRequest,
    SimulationResponse,
    WhatIfRequest,
    WhatIfResponse,
)
from app.services.physica_service import physica_service

router = APIRouter(tags=["simulation"])

@router.post("/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest, farm_data: dict[str, Any] = Depends(get_authorized_farm)) -> SimulationResponse:
    return physica_service.simulate(req)

@router.post("/what-if", response_model=WhatIfResponse)
def what_if(req: WhatIfRequest, farm_data: dict[str, Any] = Depends(get_authorized_farm)) -> WhatIfResponse:
    return physica_service.what_if(req)
