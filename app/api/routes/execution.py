from fastapi import APIRouter, HTTPException, status
from app.services.physica_service import physica_service
from app.api.schemas import PlanResponse, ApprovalRequest, ExecutionResponse

router = APIRouter()

@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: str) -> PlanResponse:
    try:
        return physica_service.get_plan(plan_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/plans/{plan_id}/approve", response_model=PlanResponse)
def approve_plan(plan_id: str, req: ApprovalRequest) -> PlanResponse:
    try:
        if req.approved:
            return physica_service.approve_plan(plan_id, req.reason)
        else:
            # Technically, reject should be mapped to a different state if we supported it fully, 
            # but for this demo, we can just say "Approval rejected".
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval required")
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post("/plans/{plan_id}/reject", response_model=PlanResponse)
def reject_plan(plan_id: str) -> PlanResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Reject not fully implemented")

@router.post("/plans/{plan_id}/dispatch", response_model=ExecutionResponse)
def dispatch_plan(plan_id: str) -> ExecutionResponse:
    try:
        return physica_service.dispatch_plan(plan_id)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        # Important: this enforces the PROPOSED -> APPROVED -> DISPATCHED state boundary!
        if "invalid state transition" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
