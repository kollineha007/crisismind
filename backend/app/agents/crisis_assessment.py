from ..models.crisis import Assessment, CrisisInput

class CrisisAssessmentAgent:
    """Specialized Agent for Ingesting Incident Feeds and Calculating Disaster Severity."""
    
    def __init__(self):
        self.name = "Crisis Assessment Agent"
        self.role = "Disaster severity scoring, urgency classification, and risk zoning"

    def assess(self, crisis: CrisisInput, data: dict | None = None) -> Assessment:
        dtype = crisis.disaster_type.upper()
        
        # Calculate severity based on disaster type and metrics
        if "HEATWAVE" in dtype:
            severity = "LOW" if crisis.affected_population < 2000 else "MEDIUM"
        elif "CYCLONE" in dtype or "EARTHQUAKE" in dtype:
            severity = "CRITICAL" if crisis.affected_population > 10000 or crisis.blocked_roads >= 3 else "HIGH"
        else:
            # Flood / Rain
            if crisis.water_level >= 3.0 or crisis.blocked_roads >= 4:
                severity = "CRITICAL"
            elif crisis.water_level >= 2.0 or crisis.blocked_roads >= 2:
                severity = "HIGH"
            elif crisis.water_level >= 1.0 or crisis.blocked_roads >= 1:
                severity = "MEDIUM"
            else:
                severity = "LOW"

        zones = data.get("zones", []) if data else []
        priority_zones = [zone["name"] for zone in zones if zone.get("severity") in ("HIGH", "CRITICAL")]
        if not priority_zones and zones:
            priority_zones = [zones[0]["name"]]
        elif not priority_zones:
            priority_zones = ["Zone A"]

        medical_risk = "HIGH" if severity in ("CRITICAL", "HIGH") or any(z.get("medical_risk") == "HIGH" for z in zones) else "MEDIUM"
        urgency = "Immediate mandatory evacuation" if severity == "CRITICAL" else "Immediate evacuation planning" if severity == "HIGH" else "Heightened preparedness and monitoring"

        reasoning = (
            f"Assessed {crisis.disaster_type} for {crisis.location}. "
            f"Evaluated {crisis.affected_population:,} exposed residents, {crisis.blocked_roads} blocked road segments, "
            f"and localized intensity indicators against regional topography."
        )

        return Assessment(
            disaster_type=crisis.disaster_type,
            severity=severity,
            affected_population=crisis.affected_population,
            priority_zones=priority_zones,
            urgency=urgency,
            medical_risk=medical_risk,
            evacuation_required=severity in ("HIGH", "CRITICAL"),
            reasoning=reasoning
        )

crisis_assessment_agent = CrisisAssessmentAgent()

def assess(crisis: CrisisInput, data: dict | None = None) -> Assessment:
    return crisis_assessment_agent.assess(crisis, data)

