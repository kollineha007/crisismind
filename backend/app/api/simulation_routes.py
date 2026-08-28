from fastapi import APIRouter, HTTPException
from ..services.crisis_service import service

router = APIRouter(prefix="/api/simulation")

@router.post("/demo-run")
async def demo_run():
    return await service.run_demo_simulation()

@router.post("/block-road")
async def block_road(road_id: str = "Route A-B (NH-65 Bypass)"):
    try:
        return await service.block_road(road_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.post("/open-road")
async def open_road(road_id: str = "Route A-B (NH-65 Bypass)"):
    return await service.set_road(road_id, "OPEN")

@router.post("/shift-state")
async def shift_state():
    """Simulate real-time environmental escalation and autonomous adaptation."""
    if not service.active:
        await service.trigger()
    # Increase water and mark a road blocked
    if service.crisis:
        service.crisis.water_level += 0.4
        service.crisis.affected_population += 1200
    return await service.block_road()

@router.post("/disable-ambulance")
async def disable_ambulance():
    ambulance = next((r for r in service.data["resources"] if "AMBULANCE" in r["type"]), None)
    if ambulance:
        ambulance["status"] = "UNAVAILABLE"
        ambulance["availability"] = False
        await service.trigger_replanning(["Ambulance asset mechanical breakdown — dispatched backup"])
    return service.current()

@router.post("/disable-bus")
async def disable_bus():
    bus = next((r for r in service.data["resources"] if "BUS" in r["type"]), None)
    if bus:
        bus["status"] = "UNAVAILABLE"
        bus["availability"] = False
        await service.trigger_replanning(["Evacuation bus fleet redirected due to debris obstruction"])
    return service.current()

@router.post("/increase-water")
async def increase_water():
    if service.crisis:
        service.crisis.water_level += 0.3
        service.crisis.affected_population += 800
        await service.trigger_replanning(["Water level surge (+0.3m) detected across low-lying riverbank"])
    return service.current()

@router.post("/new-report")
async def new_report():
    return {"accepted": True, "message": "Citizen distress report submitted to assessment triage queue"}

