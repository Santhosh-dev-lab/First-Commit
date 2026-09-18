from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_authorized_farm

router = APIRouter()

class ConnectionStatusResponse(BaseModel):
    mode: str
    status: str
    gateway_id: str | None
    last_seen: float | None

class PairingRequest(BaseModel):
    gateway_id: str
    pairing_code: str

@router.get("/settings/connectivity", response_model=ConnectionStatusResponse)
def get_connectivity(farm_data: dict[str, Any] = Depends(get_authorized_farm)):

    conn = farm_data.get("connection") or {}
    return ConnectionStatusResponse(
        mode=conn.get("mode", "CONNECT_LATER"),
        status=conn.get("status", "DISCONNECTED"),
        gateway_id=conn.get("gateway_id"),
        last_seen=conn.get("last_seen")
    )

@router.post("/gateways/pair")
def pair_gateway(req: PairingRequest, farm_data: dict[str, Any] = Depends(get_authorized_farm)):
    # This is a stub for the secure pairing workflow mentioned in the master plan
    # For now, it simply marks the gateway as paired in the database (simulated)
    # In a real system, this would provision certs and register the thing in AWS IoT
    return {"status": "success", "message": "Gateway paired successfully"}
