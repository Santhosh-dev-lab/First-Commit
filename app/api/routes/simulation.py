from fastapi import APIRouter

from app.api.schemas import (
    SimulationRequest,
    SimulationResponse,
    WhatIfRequest,
    WhatIfResponse,
)
from app.services.physica_service import physica_service

router = APIRouter()

@router.post("/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest) -> SimulationResponse:
    return physica_service.simulate(req)

@router.post("/what-if", response_model=WhatIfResponse)
def what_if(req: WhatIfRequest) -> WhatIfResponse:
    return physica_service.what_if(req)
