from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    mode: str
    agent_provider: str
    simulation: str
    digital_twin: str
    safety: str

@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    # As per instructions: If AWS mode is later enabled, distinguish MOCK from AWS_BEDROCK
    return HealthResponse(
        status="healthy",
        mode="mock",
        agent_provider="MockAgentProvider",
        simulation="available",
        digital_twin="available",
        safety="available"
    )
