from datetime import datetime, timezone
from ..models.response_plan import ResponsePlan, Recommendation

def build_plan(assessment, geo, shelter, medical, resource, version: int, changed: list[str] | None = None) -> ResponsePlan:
    changed = changed or []
    selected_route = geo["safe_routes"][0] if geo["safe_routes"] else None
    recs = [
      Recommendation(priority="P0", action=f"Use route {selected_route['id']}" if selected_route else "Hold route recommendation", reason=geo["reasoning"], affected_area="Zone A and Zone B", what="Direct evacuation through the currently safe route", data_used=[f"Route {selected_route['id']} status {selected_route['status']}" if selected_route else "No open route"], confidence=93 if selected_route else 40, alternatives=[f"Blocked or at-risk roads excluded from {len(geo['safe_routes'])} safe routes"]),
      Recommendation(priority="P0", action="Evacuate Zone A", reason="HIGH flood severity and immediate medical risk.", affected_area="Zone A", assigned_resource=resource["assignments"]["Zone A"], what="Move residents to a safe shelter", data_used=["Zone A population 2400", "HIGH severity", "safe route analysis"], confidence=94, alternatives=["Shelter A rejected: only 30 places remain"]),
      Recommendation(priority="P0", action="Evacuate Zone B", reason="HIGH flood severity with 1900 residents exposed.", affected_area="Zone B", assigned_resource=resource["assignments"]["Zone B"], what="Move residents to a safe shelter", data_used=["Zone B population 1900", "HIGH severity"], confidence=91, alternatives=["Shelter E has only 400 places remaining"]),
      Recommendation(priority="P1", action=f"Open {shelter['assignments']['Zone A']}", reason="Sufficient capacity, accessibility, and a safe route are available.", affected_area="Zone A", what="Open the assigned shelter for evacuees", data_used=[shelter["reasoning"]], confidence=90, alternatives=["Shelter A has 30 remaining places"]),
      Recommendation(priority="P1", action="Reserve hospital beds", reason=medical["reasoning"], affected_area="Vijayawada", assigned_resource=medical["hospital"], what="Reserve beds for flood-related patients", data_used=[f"{medical['available_beds']} available beds", f"{medical['icu_beds']} ICU beds"], confidence=88, alternatives=["Vijayawada General has only 8 available beds"]),
      Recommendation(priority="P1", action="Send citizen alert", reason="Residents need clear multilingual evacuation instructions.", affected_area="Zone A and Zone B", what="Notify residents of the recommended evacuation", data_used=["Assessment", "Shelter assignment", "Route status"], confidence=97, alternatives=["Emergency team briefing"]),
    ]
    return ResponsePlan(version=version, created_at=datetime.now(timezone.utc), recommendations=recs, explanation=[shelter["reasoning"], medical["reasoning"], geo["reasoning"], resource["reasoning"]], changes=changed)
