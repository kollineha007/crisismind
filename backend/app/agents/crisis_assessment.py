from ..models.crisis import Assessment, CrisisInput

def assess(crisis: CrisisInput) -> Assessment:
    severity = "CRITICAL" if crisis.water_level >= 3 else "HIGH" if crisis.water_level >= 2 else "MEDIUM"
    return Assessment(disaster_type=crisis.disaster_type, severity=severity, affected_population=crisis.affected_population, priority_zones=["Zone A", "Zone B"], urgency="Immediate evacuation planning", medical_risk="HIGH", evacuation_required=True, reasoning=f"Water level {crisis.water_level}m and {crisis.blocked_roads} blocked roads exceed the high-risk threshold.")
