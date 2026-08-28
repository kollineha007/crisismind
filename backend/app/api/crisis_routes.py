from fastapi import APIRouter, HTTPException
from ..models.crisis import CrisisInput
from ..data.demo_data import LOCATIONS
from ..services.crisis_service import service

router = APIRouter(prefix="/api/crisis")

@router.get("/current")
def current():
    return service.current()

@router.get("/locations")
def locations():
    return LOCATIONS

@router.post("/location")
async def set_location(payload: dict):
    try:
        return await service.set_location(payload.get("location_id", ""))
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.post("/trigger")
async def trigger():
    return await service.trigger()

@router.post("/analyze")
async def analyze(crisis: CrisisInput):
    return await service.analyze_crisis(crisis)

@router.post("/create")
async def create(crisis: CrisisInput):
    return await service.analyze_crisis(crisis)

@router.post("/reset")
def reset():
    service.reset()
    return service.current()

