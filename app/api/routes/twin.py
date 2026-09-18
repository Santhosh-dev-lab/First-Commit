
from fastapi import APIRouter

router = APIRouter()



@router.get("/crops")
def get_crops() -> list[dict[str, str]]:
    from domains.polyhouse.crops.registry import CropRegistry
    registry = CropRegistry.default()
    profiles = registry.all_profiles()
    return [{"crop_id": p.crop_id, "name": p.common_name} for p in profiles]
