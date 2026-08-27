from fastapi import APIRouter, HTTPException
from ..services.crisis_service import service
router=APIRouter(prefix="/api/simulation")
@router.post("/block-road")
async def block_road(road_id: str = "A-B"):
	try: return await service.block_road(road_id)
	except ValueError as exc: raise HTTPException(400,str(exc))
@router.post("/open-road")
async def open_road(): return await service.set_road("A-B", "OPEN")
@router.post("/disable-ambulance")
async def disable_ambulance():
	ambulance=next((r for r in service.data["resources"] if r["type"]=="AMBULANCE"),None)
	if ambulance: ambulance["status"]="UNAVAILABLE"; ambulance["availability"]=False
	return service.current()
@router.post("/disable-bus")
async def disable_bus():
	bus=next((r for r in service.data["resources"] if r["type"]=="BUS"),None)
	if bus: bus["status"]="UNAVAILABLE"; bus["availability"]=False
	return service.current()
@router.post("/increase-water")
async def increase_water():
	if service.crisis: service.crisis.water_level += 0.3
	return service.current()
@router.post("/new-report")
async def new_report(): return {"accepted":True,"message":"Citizen report added to assessment queue"}
