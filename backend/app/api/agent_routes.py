from fastapi import APIRouter
from ..services.crisis_service import service
router=APIRouter(prefix="/api")
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..services.crisis_service import service
from ..services.llm_service import llm_service

router=APIRouter(prefix="/api")
AGENTS=["Commander","Crisis Assessment","Geo","Shelter","Medical","Resource","Communication"]

class Assignment(BaseModel): zone: str = Field(min_length=1)
class Allocation(BaseModel): people: int = Field(gt=0)
class Beds(BaseModel): beds: int = Field(gt=0)
class Report(BaseModel): description: str = Field(min_length=3); location: str = "Vijayawada"; urgency: str = "HIGH"
class AlertRequest(BaseModel): language: str = "English"; context: str = "Flood evacuation required in Zone A"
class RejectRequest(BaseModel): reason: str = "Operator rejected recommendation"

@router.get("/state")
def state(): return service.current()
@router.get("/locations")
def locations():
	from ..data.demo_data import LOCATIONS
	return LOCATIONS
@router.get("/events")
def events(): return service.events
@router.get("/agents/status")
def agent_status(): return {"agents":[{"name":n,"status":"COMPLETED" if service.active else "WAITING","purpose":f"{n} emergency decision responsibility","current_task":"Decision analysis" if service.active else "Waiting for crisis","last_message":service.agent_logs.get(n,[{"message":"Waiting for crisis"}])[-1]["message"],"execution_count":len(service.agent_logs.get(n,[])),"logs":service.agent_logs.get(n,[])} for n in AGENTS]}
@router.get("/agents")
def agents(): return agent_status()
@router.get("/agents/{agent_id}")
def agent(agent_id: str):
	name=agent_id.replace("-"," ").title()
	if name not in AGENTS: raise HTTPException(404,"Agent not found")
	return next(a for a in agent_status()["agents"] if a["name"]==name)
@router.get("/agents/{agent_id}/logs")
def agent_logs(agent_id: str): return service.agent_logs.get(agent_id.replace("-"," ").title(),[])
@router.get("/resources")
def resources(): return service.data["resources"]
@router.post("/resources/{resource_id}/assign")
async def assign_resource(resource_id: str, body: Assignment): return await service.assign_resource(resource_id.replace("%20"," "),body.zone)
@router.post("/resources/{resource_id}/release")
async def release_resource(resource_id: str): return await service.release_resource(resource_id.replace("%20"," "))
@router.get("/shelters")
def shelters(): return service.data["shelters"]
@router.post("/shelters/{shelter_id}/allocate")
async def allocate_shelter(shelter_id: str, body: Allocation):
	try: return await service.allocate_shelter(shelter_id.replace("%20"," "),body.people)
	except ValueError as exc: raise HTTPException(400,str(exc))
@router.get("/hospitals")
def hospitals(): return service.data["hospitals"]
@router.post("/hospitals/{hospital_id}/reserve")
async def reserve_beds(hospital_id: str, body: Beds):
	try: return await service.reserve_beds(hospital_id.replace("%20"," "),body.beds)
	except ValueError as exc: raise HTTPException(400,str(exc))
@router.get("/routes")
def routes(): return service.data["roads"]
@router.post("/routes/{road_id}/block")
async def block_route(road_id: str):
	try: return {"success":True,"road_id":road_id,"status":"BLOCKED","state":await service.block_road(road_id)}
	except ValueError as exc: raise HTTPException(400,str(exc))
@router.post("/routes/{road_id}/open")
async def open_route(road_id: str):
	try: return {"success":True,"road_id":road_id,"status":"OPEN","state":await service.set_road(road_id, "OPEN")}
	except ValueError as exc: raise HTTPException(400,str(exc))
@router.get("/audit")
def audit(): return service.audit
@router.get("/audit-log")
def audit_log(): return service.audit
@router.get("/metrics")
def metrics(): return service.current()["metrics"]
@router.get("/plan/current")
def current_plan(): return service.current()["plan"]
@router.post("/plan/generate")
async def plan(): return await service.trigger()
@router.post("/plan/approve")
async def approve(): return await service.approve()
@router.post("/plan/reject")
async def reject(body: RejectRequest | None = None): return await service.reject(body.reason if body else "Operator rejected recommendation")
@router.post("/replan")
async def replan(): return await service.block_road()
@router.get("/alerts")
def alerts(): return service.alerts
@router.post("/alerts/generate")
async def generate_alert(body: AlertRequest):
	message=await llm_service.generate_alert({"context":body.context,"verified_state":service.data},body.language)
	if not message: message={"English":"Flood emergency detected. Please evacuate using the assigned safe route.","Telugu":"వరద అత్యవసర పరిస్థితి. కేటాయించిన సురక్షిత మార్గంలో ఖాళీ చేయండి.","Hindi":"बाढ़ आपातकाल। निर्धारित सुरक्षित मार्ग से जाएं।"}.get(body.language,"Flood emergency detected. Please evacuate using the assigned safe route.")
	service.add_alert(message,body.language); return service.current()
@router.post("/citizen-reports")
async def citizen_report(body: Report):
	interpretation=await llm_service.analyze_citizen_report(body.description)
	report=body.model_dump(); report["interpretation"]=interpretation or "Possible flood-related emergency; operator review required."
	return service.add_report(report)
@router.post("/simulation/reset")
def simulation_reset(): service.reset(); return service.current()
