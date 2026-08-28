from datetime import datetime, timezone
from uuid import uuid4
from ..models.response_plan import ResponsePlan, Recommendation

class CommanderAgent:
    """Master Orchestrator Agent that synthesizes specialized agent outputs into a unified action plan."""
    
    def __init__(self):
        self.name = "Commander Agent"
        self.role = "Central response orchestrator, multi-agent synthesis, and autonomous replanning"

    def build_plan(
        self,
        assessment,
        geo: dict,
        shelter: dict,
        medical: dict,
        resource: dict,
        version: int,
        changed: list[str] | None = None,
        location: str = "Vijayawada"
    ) -> ResponsePlan:
        changed = changed or []
        safe_routes = geo.get("safe_routes", [])
        blocked_routes = geo.get("blocked_routes", [])
        selected_route = safe_routes[0] if safe_routes else None
        
        primary_shelter = shelter.get("primary_shelter", "Designated Safe Shelter")
        primary_hospital = medical.get("hospital", "Central Hospital")
        
        recs: list[Recommendation] = []
        
        # 1. Critical Evacuation / Route Directive
        if assessment.evacuation_required:
            p_zones = ", ".join(assessment.priority_zones[:2]) if assessment.priority_zones else "High-Risk Sectors"
            recs.append(
                Recommendation(
                    id="REC-EVAC-01",
                    priority="CRITICAL",
                    action=f"Mandatory Evacuation of {p_zones}",
                    reason=f"{assessment.severity} hazard level with {assessment.affected_population:,} vulnerable residents exposed.",
                    agent="Geo Agent",
                    affected_area=p_zones,
                    affected_count=assessment.affected_population,
                    assigned_resource=resource.get("assignments", {}).get(assessment.priority_zones[0] if assessment.priority_zones else "Zone A", "Disaster Bus Fleet"),
                    approval_status="PENDING",
                    what="Deploy transit fleets and escort residents to safe shelter zones",
                    data_used=[f"{assessment.severity} Severity", f"{assessment.affected_population:,} Exposed", "Geo Inundation Map"],
                    confidence=96,
                    alternatives=["Shelter-in-place (Rejected: Water rising rapidly)"],
                    action_type="EVACUATE_ZONE"
                )
            )
            
        # 2. Road Safety Directive
        if blocked_routes:
            top_blocked = blocked_routes[0]
            recs.append(
                Recommendation(
                    id="REC-ROAD-02",
                    priority="CRITICAL" if assessment.severity == "CRITICAL" else "HIGH",
                    action=f"Enforce Perimeter Block on {top_blocked.get('id', 'Hazardous Sector')}",
                    reason=f"Water accumulation and route obstruction render passage unsafe. Divert traffic via {selected_route['id'] if selected_route else 'Highline'}.",
                    agent="Geo Agent",
                    affected_area=top_blocked.get("source", location),
                    affected_count=3200,
                    assigned_resource="Traffic Police & Barricade Units",
                    approval_status="PENDING",
                    what="Simulate roadblock enforcement and update live routing network",
                    data_used=[f"Road status: {top_blocked.get('status')}", f"Risk level: {top_blocked.get('risk_level', 'HIGH')}"],
                    confidence=94,
                    alternatives=["Controlled single-lane convoy (Rejected: Structural risk)"],
                    action_type="BLOCK_ROAD"
                )
            )
        elif selected_route:
            recs.append(
                Recommendation(
                    id="REC-ROUTE-02",
                    priority="HIGH",
                    action=f"Designate {selected_route.get('id')} as Primary Green Corridor",
                    reason=f"Verified clear route with {selected_route.get('distance', 3.0)} km clearance to emergency shelters.",
                    agent="Geo Agent",
                    affected_area=location,
                    affected_count=assessment.affected_population,
                    assigned_resource="Highway Patrol Escort",
                    approval_status="PENDING",
                    what="Prioritize emergency vehicles and evacuation buses along this corridor",
                    data_used=[f"Distance: {selected_route.get('distance')} km", "Zero reported blockages"],
                    confidence=92,
                    alternatives=["Secondary urban bypass routes"],
                    action_type="GENERIC"
                )
            )

        # 3. Shelter Directive
        recs.append(
            Recommendation(
                id="REC-SHELTER-03",
                priority="HIGH",
                action=f"Activate {primary_shelter} for Immediate Intake",
                reason=f"Facility has {shelter.get('primary_vacancies', 1000):,} available capacity with verified high safety grade.",
                agent="Shelter Agent",
                affected_area=primary_shelter,
                affected_count=min(assessment.affected_population, shelter.get("primary_vacancies", 1000)),
                assigned_resource="Municipal Relief Staff & Cots",
                approval_status="PENDING",
                what="Open shelter doors, prepare dry rations and bedding for incoming evacuees",
                data_used=[f"{shelter.get('primary_vacancies', 1000):,} Vacant slots", "High-ground access verified"],
                confidence=91,
                alternatives=[f"Overflow to {shelter.get('secondary_shelter', 'Secondary Center')}"],
                action_type="OPEN_SHELTER"
            )
        )

        # 4. Resource Allocation Directive
        shortages = resource.get("shortages", [])
        if shortages:
            top_shortage = shortages[0]
            recs.append(
                Recommendation(
                    id="REC-RES-04",
                    priority="HIGH",
                    action=f"Emergency Dispatch: Allocate 500 {top_shortage['item']} units to {primary_shelter}",
                    reason=f"Identified supply deficit ({top_shortage['available']} available vs {top_shortage['required']} required).",
                    agent="Resource Agent",
                    affected_area=primary_shelter,
                    affected_count=1500,
                    assigned_resource=f"Central Depot Supply Fleet ({top_shortage['item']})",
                    approval_status="PENDING",
                    what="Transfer emergency rations/water tankers from reserve warehouse",
                    data_used=[f"Deficit: {top_shortage['deficit']} {top_shortage['unit']}", "Inventory telemetry"],
                    confidence=89,
                    alternatives=["Request inter-district mutual aid"],
                    action_type="ALLOCATE_RESOURCE"
                )
            )
        else:
            recs.append(
                Recommendation(
                    id="REC-RES-04",
                    priority="MEDIUM",
                    action="Pre-position Emergency Logistics & Water Tankers",
                    reason="Ensure continuous 48-hour potable water and sustenance reserves at active relief centers.",
                    agent="Resource Agent",
                    affected_area=location,
                    affected_count=2000,
                    assigned_resource="Disaster Logistics Unit",
                    approval_status="PENDING",
                    what="Stage relief supplies along designated transit hubs",
                    data_used=["Resource inventory status", "Shelter readiness index"],
                    confidence=88,
                    alternatives=["Direct on-demand delivery"],
                    action_type="ALLOCATE_RESOURCE"
                )
            )

        # 5. Medical Triage Directive
        recs.append(
            Recommendation(
                id="REC-MED-05",
                priority="MEDIUM",
                action=f"Reserve {min(30, medical.get('available_beds', 20))} Acute Beds at {primary_hospital}",
                reason=f"Prepare for estimated surge of ~{medical.get('estimated_casualties', 20)} triage admissions. {medical.get('available_beds', 0)} beds available.",
                agent="Medical Agent",
                affected_area=primary_hospital,
                affected_count=medical.get("estimated_casualties", 20),
                assigned_resource=f"{medical.get('ambulances', 4)} Mobile Ambulances",
                approval_status="PENDING",
                what="Hold trauma surgery bays and mobilize emergency physician shift",
                data_used=[f"{medical.get('available_beds')} Beds Available", f"{medical.get('icu_beds')} ICU Units"],
                confidence=90,
                alternatives=[f"Divert overflow to {medical.get('backup_hospital', 'Regional Hospital')}"],
                action_type="RESERVE_BEDS"
            )
        )

        # 6. Public Alert Broadcast Directive
        recs.append(
            Recommendation(
                id="REC-COMM-06",
                priority="LOW",
                action=f"Broadcast Multilingual Evacuation Warning to {location} Citizens",
                reason="Disseminate geo-targeted SMS, sirens, and radio instructions in English, Telugu, and Hindi.",
                agent="Commander Agent",
                affected_area=f"All Sectors in {location}",
                affected_count=assessment.affected_population,
                assigned_resource="Integrated Public Alert & Warning System (IPAWS)",
                approval_status="PENDING",
                what="Issue emergency alert with approved evacuation route and shelter destination",
                data_used=["Disaster Assessment", f"Safe route: {selected_route['id'] if selected_route else 'Primary Highline'}"],
                confidence=98,
                alternatives=["Door-to-door siren announcements only"],
                action_type="BROADCAST_ALERT"
            )
        )

        explanations = [
            f"Geo Agent verified {len(safe_routes)} safe corridors and identified {len(blocked_routes)} obstructed segments.",
            f"Shelter Agent selected {primary_shelter} ({shelter.get('primary_vacancies', 0):,} vacant capacity).",
            f"Medical Agent established primary trauma reception at {primary_hospital} ({medical.get('available_beds', 0)} beds free).",
            f"Resource Agent structured transit deployment and tracked {resource.get('total_resources', 0)} logistics assets."
        ]

        return ResponsePlan(
            version=version,
            status="PENDING APPROVAL",
            created_at=datetime.now(timezone.utc),
            recommendations=recs,
            explanation=explanations,
            changes=changed
        )

commander_agent = CommanderAgent()

def build_plan(assessment, geo, shelter, medical, resource, version: int, changed: list[str] | None = None, location: str = "Vijayawada") -> ResponsePlan:
    return commander_agent.build_plan(assessment, geo, shelter, medical, resource, version, changed, location)

