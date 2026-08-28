from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..services.crisis_service import service
from ..services.llm_service import llm_service

router = APIRouter(prefix="/api")

AGENTS = [
    "Commander Agent",
    "Crisis Assessment Agent",
    "Geo Agent",
    "Shelter Agent",
    "Medical Agent",
    "Resource Agent",
    "Communication Agent"
]

AGENT_ROLES = {
    "Commander Agent": {
        "role": "Master Orchestration & Adaptive Re-Planning",
        "purpose": "Coordinates specialized domain agents, consolidates tactical findings, synthesizes explainable action plans, and triggers autonomous re-planning cycles upon situation shifts."
    },
    "Crisis Assessment Agent": {
        "role": "Disaster Severity Scoring & Population Impact Analysis",
        "purpose": "Calculates emergency severity indices, evaluates exposed demographics, determines evacuation necessity, and sets baseline operational priority zones."
    },
    "Geo Agent": {
        "role": "Geographic Topology & Route Accessibility Analysis",
        "purpose": "Monitors road networks, detects flood-submerged or blocked segments, identifies high-risk bottleneck routes, and calculates safe green evacuation corridors."
    },
    "Shelter Agent": {
        "role": "Relief Shelter Capacity Matching & Safety Grading",
        "purpose": "Tracks shelter vacancies, evaluates ingress safety and elevation headroom, and matches displaced zone populations to optimal safe receiving facilities."
    },
    "Medical Agent": {
        "role": "Hospital Capacity, Trauma Readiness & Triage Logistics",
        "purpose": "Monitors regional bed availability, audits ICU and ambulance assets, projects casualty surge rates, and reserves critical trauma capacity."
    },
    "Resource Agent": {
        "role": "Emergency Inventory Tracking & Multi-Zone Logistics Dispatch",
        "purpose": "Audits potable water, food rations, medical kits, rescue boats, and transit fleets, detecting supply deficits and executing logistics allocation."
    },
    "Communication Agent": {
        "role": "Multilingual Citizen Emergency Broadcasts",
        "purpose": "Generates verified emergency guidance alerts in English, Telugu, and Hindi for public alert networks, SMS broadcasts, and field operators."
    }
}

class Assignment(BaseModel):
    zone: str = Field(min_length=1)

class Allocation(BaseModel):
    people: int = Field(gt=0)

class ResourceAllocation(BaseModel):
    resource_type: str = "POTABLE WATER"
    quantity: int = Field(gt=0)
    target: str = "Shelter"

class Beds(BaseModel):
    beds: int = Field(gt=0)

class Report(BaseModel):
    description: str = Field(min_length=3)
    location: str = "Vijayawada"
    urgency: str = "HIGH"

class AlertRequest(BaseModel):
    language: str = "English"
    context: str = "Flood evacuation required in Zone A"

class RejectRequest(BaseModel):
    reason: str = "Operator rejected recommendation"

@router.get("/state")
def state():
    return service.current()

@router.get("/locations")
def locations():
    from ..data.demo_data import LOCATIONS
    return LOCATIONS

@router.get("/events")
def events():
    return service.events

@router.get("/recommendations")
def recommendations():
    return service.current().get("plan", {}).get("recommendations", []) if service.plan else []

@router.get("/agents/status")
def agent_status():
    res = []
    for name in AGENTS:
        meta = AGENT_ROLES.get(name, {"role": "Autonomous Emergency Agent", "purpose": "Decision intelligence"})
        state_info = service.agent_states.get(name, {
            "name": name,
            "status": "WAITING",
            "last_message": "Standby — waiting for incident activation",
            "execution_count": 0
        })
        res.append({
            **state_info,
            "role": meta["role"],
            "purpose": meta["purpose"],
            "current_task": state_info["last_message"] if service.active else "Standby — monitoring telemetry feeds"
        })
    return {"agents": res}

@router.get("/agents")
def agents():
    return agent_status()

@router.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    name = agent_id.replace("-", " ").title()
    if not name.endswith("Agent") and name in ("Commander", "Crisis Assessment", "Geo", "Shelter", "Medical", "Resource", "Communication"):
        name += " Agent"
    all_agents = agent_status()["agents"]
    matched = next((a for a in all_agents if a["name"].lower() == name.lower() or a["name"].lower().startswith(agent_id.lower())), None)
    if not matched:
        raise HTTPException(404, f"Agent '{agent_id}' not found")
    return matched

@router.get("/agents/{agent_id}/logs")
def agent_logs(agent_id: str):
    name = agent_id.replace("-", " ").title()
    if not name.endswith("Agent") and name in ("Commander", "Crisis Assessment", "Geo", "Shelter", "Medical", "Resource", "Communication"):
        name += " Agent"
    return service.agent_logs.get(name, [])

@router.post("/actions/{action_id}/approve")
async def approve_single_action(action_id: str):
    try:
        return await service.approve_action(action_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.post("/actions/{action_id}/reject")
async def reject_single_action(action_id: str, body: RejectRequest | None = None):
    try:
        return await service.reject_action(action_id, body.reason if body else "Operator rejected recommendation")
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.post("/actions/{action_id}/execute")
async def execute_single_action(action_id: str):
    try:
        return await service.approve_action(action_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.get("/resources")
def resources():
    return service.data["resources"]

@router.post("/resources/{resource_id}/assign")
async def assign_resource(resource_id: str, body: Assignment):
    return await service.assign_resource(resource_id.replace("%20", " "), body.zone)

@router.post("/resources/{resource_id}/release")
async def release_resource(resource_id: str):
    return await service.release_resource(resource_id.replace("%20", " "))

@router.post("/resources/allocate")
async def allocate_resource_custom(body: ResourceAllocation):
    item = next((r for r in service.data["resources"] if body.resource_type in r["type"]), None)
    if item and item["quantity_available"] >= body.quantity:
        item["quantity_available"] -= body.quantity
        await service.emit("Resource Agent", "COMPLETED", f"Allocated {body.quantity} units of {body.resource_type} to {body.target}", "RESOURCE_ASSIGNED")
        await service.trigger_replanning([f"Dispatched {body.quantity} {body.resource_type} to {body.target}"])
    return service.current()

@router.get("/shelters")
def shelters():
    return service.data["shelters"]

@router.post("/shelters/{shelter_id}/allocate")
async def allocate_shelter(shelter_id: str, body: Allocation):
    try:
        return await service.allocate_shelter(shelter_id.replace("%20", " "), body.people)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.get("/hospitals")
def hospitals():
    return service.data["hospitals"]

@router.post("/hospitals/{hospital_id}/reserve")
async def reserve_beds(hospital_id: str, body: Beds):
    try:
        return await service.reserve_beds(hospital_id.replace("%20", " "), body.beds)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.get("/routes")
def routes():
    return service.data["roads"]

@router.post("/routes/{road_id}/block")
async def block_route(road_id: str):
    try:
        return {"success": True, "road_id": road_id, "status": "BLOCKED", "state": await service.block_road(road_id)}
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.post("/routes/{road_id}/open")
async def open_route(road_id: str):
    try:
        return {"success": True, "road_id": road_id, "status": "OPEN", "state": await service.set_road(road_id, "OPEN")}
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.get("/audit")
def audit():
    return service.audit

@router.get("/audit-log")
def audit_log():
    return service.audit

@router.get("/metrics")
def metrics():
    return service.current()["metrics"]

@router.get("/plan/current")
def current_plan():
    return service.current()["plan"]

@router.post("/plan/generate")
async def plan():
    return await service.trigger()

@router.post("/plan/approve")
async def approve():
    return await service.approve_all_plan()

@router.post("/plan/reject")
async def reject(body: RejectRequest | None = None):
    return await service.reject_all_plan(body.reason if body else "Operator rejected recommendation")

@router.post("/replan")
async def replan():
    return await service.trigger_replanning()

@router.get("/alerts")
def alerts():
    return service.alerts

@router.post("/alerts/generate")
async def generate_alert(body: AlertRequest):
    message = await llm_service.generate_alert({"context": body.context, "verified_state": service.data}, body.language)
    if not message:
        message = {
            "English": "EMERGENCY BROADCAST: Flash flooding detected. Evacuate immediately using designated safe corridors to municipal shelters.",
            "Telugu": "అత్యవసర సమాచారం: వరద తీవ్రత పెరుగుతోంది. దయచేసి కేటాయించిన సురక్షిత మార్గంలో ఆశ్రయ కేంద్రాలకు వెళ్లండి.",
            "Hindi": "आपातकालीन चेतावनी: बाढ़ का पानी बढ़ रहा है। कृपया निर्धारित सुरक्षित मार्ग से नजदीकी राहत शिविर में जाएं।"
        }.get(body.language, "Emergency evacuation instructions issued. Follow designated safe routes.")
    service.add_alert(message, body.language)
    return service.current()

@router.post("/citizen-reports")
async def citizen_report(body: Report):
    interpretation = await llm_service.analyze_citizen_report(body.description)
    report = body.model_dump()
    report["interpretation"] = interpretation or "Possible localized inundation distress; dispatched for tactical validation."
    return service.add_report(report)

@router.post("/simulation/reset")
def simulation_reset():
    service.reset()
    return service.current()

