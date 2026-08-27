from fastapi import APIRouter
from ..models.crisis import CrisisInput
from ..services.planning_service import generate
from ..data.demo_data import LOCATIONS
from ..services.crisis_service import service
router=APIRouter(prefix="/api/crisis")
@router.get("/current")
def current(): return service.current()
@router.get("/locations")
def locations(): return LOCATIONS
@router.post("/location")
async def set_location(payload: dict):
	try: return await service.set_location(payload.get("location_id", ""))
	except ValueError as exc: from fastapi import HTTPException; raise HTTPException(400, str(exc))
@router.post("/trigger")
async def trigger(): return await service.trigger()
@router.post("/analyze")
async def analyze(crisis: CrisisInput):
	service.crisis=crisis
	service.active=True
	service.version=max(service.version,1)
	service.assessment,geo,shelter,medical,resource,service.plan=generate(crisis,service.data,service.version)
	return service.current()
@router.post("/reset")
def reset(): service.reset(); return service.current()
