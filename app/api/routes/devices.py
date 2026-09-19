from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_authorized_farm

router = APIRouter()

class DeviceResponse(BaseModel):
    id: str
    name: str
    device_type: str
    zone_id: str | None
    status: str
    last_seen: float | None

@router.get("/devices", response_model=list[DeviceResponse])
def get_devices(farm_data: dict[str, Any] = Depends(get_authorized_farm)):

    # In a real system, we would parse metadata properly
    devices = []
    for d in farm_data.get("devices", []):
        devices.append(DeviceResponse(
            id=d["id"],
            name=d["name"],
            device_type=d["device_type"],
            zone_id=d.get("zone_id"),
            status=d.get("status", "UNKNOWN"),
            last_seen=d.get("last_seen")
        ))
    return devices
