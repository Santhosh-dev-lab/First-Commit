from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_authorized_farm
from app.api.schemas import AgentTraceResponse, IntentRequest, IntentResponse
from app.services.physica_service import physica_service

router = APIRouter()

@router.post("/intent", response_model=IntentResponse)
def submit_intent(req: IntentRequest, farm_data: dict[str, Any] = Depends(get_authorized_farm)) -> IntentResponse:
    return physica_service.submit_intent(req, farm_data["farm"]["id"])

@router.get("/agents/{run_id}", response_model=AgentTraceResponse)
def get_agent_trace(run_id: str) -> AgentTraceResponse:
    from fastapi import HTTPException

    from app.services.repositories import agent_trace_repo
    
    trace = agent_trace_repo.get(run_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Agent trace not found")
        
    return AgentTraceResponse(
        run_id=trace.agent_run_id,
        agent_type=trace.agent_type,
        status=trace.execution_status,
        tools_called=trace.tools_called,
        evidence=None, # mapping evidence explicitly omitted for brevity
        decision=trace.decision,
        execution_state=trace.execution_status
    )
