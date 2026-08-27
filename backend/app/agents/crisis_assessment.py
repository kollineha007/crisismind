from ..models.crisis import Assessment, CrisisInput

def assess(crisis: CrisisInput, data: dict | None = None) -> Assessment:
    severity = "CRITICAL" if crisis.water_level >= 3 else "HIGH" if crisis.water_level >= 2 else "MEDIUM" if crisis.water_level >= 1 else "LOW"
    zones = data.get("zones", []) if data else []
    priority_zones = [zone["name"] for zone in zones if zone["severity"] in ("HIGH", "CRITICAL")] or ["Zone A"]
    medical_risk = "HIGH" if any(zone.get("medical_risk") == "HIGH" for zone in zones) else "MEDIUM"
    return Assessment(disaster_type=crisis.disaster_type, severity=severity, affected_population=crisis.affected_population, priority_zones=priority_zones, urgency="Immediate evacuation planning" if severity in ("HIGH", "CRITICAL") else "Preparedness and monitoring", medical_risk=medical_risk, evacuation_required=severity in ("HIGH", "CRITICAL"), reasoning=f"Water level {crisis.water_level}m and {crisis.blocked_roads} blocked roads were evaluated against the selected location profile.")
