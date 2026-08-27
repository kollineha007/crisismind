from datetime import datetime, timezone
from uuid import uuid4
from ..data.demo_data import LOCATIONS, LOCATION_PROFILES, snapshot
from ..models.crisis import CrisisInput
from .planning_service import generate
from .websocket_manager import manager
from .llm_service import llm_service
from .event_manager import EventManager

class CrisisService:
    def __init__(self): self.reset()
    def reset(self):
        self.location=LOCATIONS[0].copy(); self.data=snapshot(); self.crisis=None; self.assessment=None; self.plan=None; self.previous_plan=None; self.version=0; self.audit=[]; self.events=[]; self.event_manager=EventManager(); self.active=False; self.alerts=[]; self.reports=[]; self.agent_logs={}; self.agent_states={}; self.created_at=None; self.updated_at=None
    async def emit(self, agent, status, message, event_type, data=None):
        now=datetime.now(timezone.utc).isoformat(); normalized="RUNNING" if status=="WORKING" else "COMPLETED" if status=="COMPLETE" else status; event=await self.event_manager.publish(event_type,agent.upper().replace(" ","_"),message,self.location["name"],agent,"WARNING" if status=="WARNING" else "INFO",data,normalized); event.update({"input_summary":message if status=="WORKING" else "","output_summary":message if status=="COMPLETE" else "","duration":0,"crisis_id":self.crisis.get("id") if isinstance(self.crisis,dict) else None}); self.events.append(event); self.updated_at=now; self.agent_logs.setdefault(agent,[]).append(event); self.agent_states[agent]={"name":agent,"status":normalized,"last_message":message,"last_started":now if status=="WORKING" else self.agent_states.get(agent,{}).get("last_started"),"last_completed":now if status=="COMPLETE" else self.agent_states.get(agent,{}).get("last_completed"),"execution_count":len(self.agent_logs[agent])}; return event
    async def set_location(self, location_id):
        selected=next((item for item in LOCATIONS if item["id"]==location_id),None)
        if selected is None and str(location_id).startswith("custom:"):
            selected={"id":"custom","name":str(location_id).split(":",1)[1].strip(),"state":"Custom","latitude":LOCATIONS[0]["latitude"],"longitude":LOCATIONS[0]["longitude"]}
        if selected is None: raise ValueError("Unknown location")
        previous=self.location["name"]; self.location=selected.copy(); self.data=snapshot(location_id); self.crisis=None; self.assessment=None; self.plan=None; self.previous_plan=None; self.version=0; self.active=False; self._audit("Emergency Operator","Location changed",[previous,selected["name"]],"LOCATION_CHANGED"); await self.emit("Crisis Manager","COMPLETE",f"Location changed from {previous} to {selected['name']}","LOCATION_CHANGED"); await self.emit("System","COMPLETE","Shared location and simulation data updated","STATE_UPDATED"); return self.current()
    async def trigger(self):
        profile=LOCATION_PROFILES.get(self.location["id"],LOCATION_PROFILES["vijayawada"]); population=sum(zone["population"] for zone in self.data["zones"]); self.active=True; self.created_at=datetime.now(timezone.utc).isoformat(); self.crisis=CrisisInput(location=self.location["name"],water_level=profile["water_level"],affected_population=population,blocked_roads=len([road for road in self.data["roads"] if road["status"]=="BLOCKED"]),timestamp=datetime.now(timezone.utc)); self._audit("Crisis Manager","Crisis created",[self.location["name"],self.crisis.disaster_type],"CRISIS_CREATED"); await self.emit("Crisis Manager","WORKING",f"Received flood report for {self.location['name']}","CRISIS_CREATED")
        for agent,msg,event_type in [("Crisis Assessment","Assessing severity and medical risk","ASSESSMENT_STARTED"),("Geo","Analyzing 8 roads and safe routes","GEO_ANALYSIS_STARTED"),("Shelter","Evaluating 5 shelters","SHELTER_ANALYSIS_STARTED"),("Medical","Evaluating 4 hospitals","MEDICAL_ANALYSIS_STARTED"),("Resource","Checking 10 emergency resources","RESOURCE_ANALYSIS_STARTED"),("Communication","Preparing multilingual alerts","AGENT_STARTED")]:
            await self.emit(agent,"WORKING",msg,event_type)
        self.version=1; self.assessment,geo,shelter,medical,resource,self.plan=generate(self.crisis,self.data,self.version)
        llm_reasoning=await llm_service.analyze_crisis({"crisis":self.crisis.model_dump(mode="json"),"zones":self.data["zones"],"roads":self.data["roads"]})
        if llm_reasoning: self.assessment.reasoning=llm_reasoning
        plan_reasoning=await llm_service.generate_plan_reasoning({"assessment":self.assessment.model_dump(),"shelters":self.data["shelters"],"hospitals":self.data["hospitals"],"resources":self.data["resources"]})
        explanation=await llm_service.generate_explanation({"assessment":self.assessment.model_dump(),"plan":self.plan.model_dump()})
        if plan_reasoning: self.plan.explanation.insert(0,plan_reasoning)
        if explanation: self.plan.explanation.append(explanation)
        alert=await llm_service.generate_alert({"assessment":self.assessment.model_dump(),"plan":self.plan.model_dump()},"English")
        if alert: self.add_alert(alert,"English")
        for agent,event_type in [("Crisis Assessment","ASSESSMENT_COMPLETED"),("Geo","GEO_ANALYSIS_COMPLETED"),("Shelter","SHELTER_ANALYSIS_COMPLETED"),("Medical","MEDICAL_ANALYSIS_COMPLETED"),("Resource","RESOURCE_ANALYSIS_COMPLETED"),("Communication","AGENT_COMPLETED")]: await self.emit(agent,"COMPLETE","Analysis complete",event_type)
        await self.emit("Commander","COMPLETE","Response plan generated; operator approval required","COMMANDER_COMPLETED"); self._audit("Commander","Plan generated",["structured demo data"],"PLAN_GENERATED"); await self.emit("Commander","COMPLETE","Operator approval required","PLAN_APPROVAL_REQUIRED"); return self.current()
    async def block_road(self, road_id="A-B"):
        if not self.active or not self.plan: raise ValueError("Trigger a crisis before blocking a road")
        road=next((r for r in self.data["roads"] if r["id"]==road_id),None)
        if road is None: raise ValueError(f"Road {road_id} does not exist")
        if road["status"]=="BLOCKED": raise ValueError("Road is already blocked")
        self.previous_plan=self.plan.model_copy(deep=True); road["status"]="BLOCKED"; self._audit("Emergency Operator","Road blocked",[road_id],"ROAD_BLOCKED"); await self.emit("Emergency Operator","WARNING",f"Road {road_id} is now BLOCKED. Previous plan is no longer optimal.","ROAD_BLOCKED"); await self.emit("System","WARNING","Shared route state updated","STATE_UPDATED"); await self.emit("Commander","WORKING","Generating alternative response plan","REPLANNING_STARTED")
        for agent in ["Geo","Shelter","Resource","Medical","Commander"]: await self.emit(agent,"WORKING",f"Replanning after {road_id} became unavailable","AGENT_STARTED")
        self.version+=1; self.assessment,geo,shelter,medical,resource,self.plan=generate(self.crisis,self.data,self.version,True,[f"Route {road_id} unavailable; alternative route selected","Shelter assignment re-evaluated","Resource assignment re-evaluated"]); llm_reasoning=await llm_service.generate_plan_reasoning({"roads":self.data["roads"],"shelters":self.data["shelters"],"resources":self.data["resources"]});
        if llm_reasoning: self.plan.explanation.insert(0,llm_reasoning)
        await self.emit("Geo","COMPLETE",f"Route {road_id} unavailable; alternative route found","AGENT_COMPLETED"); await self.emit("Shelter","COMPLETE","Re-evaluated shelter capacity","AGENT_COMPLETED"); await self.emit("Resource","COMPLETE","Reallocated available resources","AGENT_COMPLETED"); await self.emit("Medical","COMPLETE","Re-evaluated hospital capacity","AGENT_COMPLETED"); await self.emit("Commander","COMPLETE","New response plan generated; approval required","PLAN_GENERATED"); self._audit("Commander","Replanned after road blockage",self.plan.changes,"REPLANNING_COMPLETED"); await self.emit("Commander","COMPLETE","Replanning completed","REPLANNING_COMPLETED"); await self.emit("System","COMPLETE","Shared state updated after replanning","STATE_UPDATED"); return self.current()
    async def approve(self):
        if self.plan: self.plan.status="APPROVED"; [setattr(r,"approval_status","APPROVED") for r in self.plan.recommendations]; self._audit("Emergency Operator","Approved plan",[r.action for r in self.plan.recommendations],"PLAN_APPROVED"); await self.emit("Emergency Operator","COMPLETE","Plan approved by trained operator","PLAN_APPROVED")
        return self.current()
    async def reject(self, reason="Operator rejected recommendation"):
        if self.plan: self.plan.status="REJECTED"; self._audit("Emergency Operator",reason,[],"PLAN_REJECTED"); await self.emit("Emergency Operator","WARNING",reason,"PLAN_REJECTED")
        return self.current()
    async def assign_resource(self, resource_id, zone):
        resource=next((r for r in self.data["resources"] if r["id"]==resource_id),None)
        if resource and resource["status"] != "UNAVAILABLE": resource.update(status="ASSIGNED", assigned_zone=zone); self._audit("Emergency Operator","Assigned resource",[resource_id,zone],"RESOURCE_ASSIGNED"); await self.emit("Resource Agent","COMPLETE",f"{resource_id} assigned to {zone}","RESOURCE_ASSIGNED")
        return self.current()
    async def release_resource(self, resource_id):
        resource=next((r for r in self.data["resources"] if r["id"]==resource_id),None)
        if resource: resource.update(status="AVAILABLE", assigned_zone=None); self._audit("Emergency Operator","Released resource",[resource_id],"RESOURCE_RELEASED")
        return self.current()
    async def allocate_shelter(self, shelter_name, people):
        shelter=next((s for s in self.data["shelters"] if s["name"]==shelter_name),None)
        if not shelter or people < 1 or people > shelter["capacity"]-shelter["occupancy"]: raise ValueError("Evacuee count exceeds remaining shelter capacity")
        shelter["occupancy"] += people; self._audit("Emergency Operator","Allocated evacuees",[shelter_name,str(people)],"SHELTER_UPDATED"); await self.emit("Shelter Agent","COMPLETE",f"{people} evacuees allocated to {shelter_name}","SHELTER_UPDATED"); return self.current()
    async def reserve_beds(self, hospital_name, beds):
        hospital=next((h for h in self.data["hospitals"] if h["name"]==hospital_name),None)
        if not hospital or beds < 1 or beds > hospital["available_beds"]: raise ValueError("Requested beds exceed current availability")
        hospital["available_beds"] -= beds; self._audit("Emergency Operator","Reserved hospital beds",[hospital_name,str(beds)],"HOSPITAL_UPDATED"); await self.emit("Medical Agent","COMPLETE",f"{beds} beds reserved at {hospital_name}","HOSPITAL_UPDATED"); return self.current()
    async def set_road(self, road_id, status):
        road=next((r for r in self.data["roads"] if r["id"]==road_id),None)
        if road is None: raise ValueError(f"Road {road_id} does not exist")
        if road["status"]==status: raise ValueError("Road is already blocked" if status=="BLOCKED" else "Road is already open")
        road["status"]=status; event="ROAD_BLOCKED" if status=="BLOCKED" else "ROAD_OPENED"; self._audit("Emergency Operator",f"Road {status.lower()}",[road_id],event); await self.emit("Geo","WARNING" if status=="BLOCKED" else "COMPLETE",f"Road {road_id} is {status}",event); await self.emit("System","COMPLETE","Shared route state updated","STATE_UPDATED")
        return self.current()
    def add_report(self, report): self.reports.append(report); self._audit("Emergency Operator","Added citizen report",[report.get("description","")],"CITIZEN_REPORT_ADDED"); return self.current()
    def add_alert(self, message, language="English"):
        alert={"id":f"ALERT-{len(self.alerts)+1:03}","type":"Emergency","message":message,"language":language,"priority":"HIGH","created_at":datetime.now(timezone.utc).isoformat(),"status":"DRAFT"}; self.alerts.append(alert); self._audit("Communication Agent","Generated alert",[language],"ALERT_CREATED"); return self.current()
    def _audit(self,agent,action,data,event): self.audit.append({"id":str(uuid4()),"timestamp":datetime.now(timezone.utc).isoformat(),"agent":agent,"actor":agent,"action":action,"description":action,"reason":"Decision-support recommendation from verified simulation state","data_used":data,"metadata":{"location":self.location["name"]},"location":self.location["name"],"plan_version":self.version,"human_approval":self.plan.status if self.plan else "N/A","event_type":event})
    def current(self):
        total_capacity=sum(s["capacity"] for s in self.data["shelters"]); occupied=sum(s["occupancy"] for s in self.data["shelters"]); active_resources=sum(r["status"]!="UNAVAILABLE" for r in self.data["resources"]); assigned=sum(r["status"]=="ASSIGNED" for r in self.data["resources"])
        metrics={"planning_time_seconds":0 if not self.active else 1,"replanning_time_seconds":0 if self.version<2 else 1,"shelter_utilization":round(occupied/total_capacity*100),"resource_utilization":round(assigned/active_resources*100) if active_resources else 0,"affected_population_covered":4300 if self.active else 0,"available_hospital_capacity":sum(h["available_beds"] for h in self.data["hospitals"]),"route_distance_km":sum(r["distance"] for r in self.data["roads"] if r["status"]=="OPEN")/max(1,len([r for r in self.data["roads"] if r["status"]=="OPEN"])),"available_buses":sum(r["status"]=="AVAILABLE" and r["type"]=="BUS" for r in self.data["resources"]),"available_ambulances":sum(r["status"]=="AVAILABLE" and r["type"]=="AMBULANCE" for r in self.data["resources"]),"agent_executions":len(self.events),"plan_versions":self.version,"human_approvals":len([a for a in self.audit if a["event_type"]=="PLAN_APPROVED"]),"total_crises":len([a for a in self.audit if a["event_type"]=="CRISIS_CREATED"]),"active_crisis":self.active,"total_events":len(self.events),"blocked_roads":len([r for r in self.data["roads"] if r["status"]=="BLOCKED"]),"plans_generated":self.version,"plans_replanned":max(0,self.version-1),"gemini_requests":0,"gemini_failures":0,"average_agent_execution_time":0}
        return {"active":self.active,"demo_mode":not llm_service.active,"ai_mode":"REAL AI - GEMINI" if llm_service.active else "DEMO MODE - FALLBACK AI","location":self.location,"crisis":self.crisis.model_dump(mode="json") if self.crisis else None,"assessment":self.assessment.model_dump() if self.assessment else None,"plan":self.plan.model_dump(mode="json") if self.plan else None,"previous_plan":self.previous_plan.model_dump(mode="json") if self.previous_plan else None,"data":self.data,"events":self.events,"audit":self.audit,"alerts":self.alerts,"reports":self.reports,"agent_logs":self.agent_logs,"agent_states":self.agent_states,"created_at":self.created_at,"updated_at":self.updated_at,"metrics":metrics}
service=CrisisService()
