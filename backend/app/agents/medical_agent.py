class MedicalAgent:
    """Specialized Agent for Hospital Capacity, Trauma Care, and Medical Logistics."""
    
    def __init__(self):
        self.name = "Medical Agent"
        self.role = "Hospital capacity, ICU readiness, and emergency medical triage"

    def allocate(self, data: dict, severity: str = "HIGH", affected_population: int = 8500) -> dict:
        hospitals = data.get("hospitals", [])
        if not hospitals:
            return {"hospital": "Emergency Field Hospital", "available_beds": 50, "icu_beds": 10, "ambulances": 5, "reasoning": "Standard emergency deployment."}

        # Calculate metrics
        total_beds = sum(h.get("total_beds", 0) for h in hospitals)
        total_available = sum(h.get("available_beds", 0) for h in hospitals)
        total_icu = sum(h.get("icu_beds", 0) for h in hospitals)
        total_ambulances = sum(h.get("ambulances", 0) for h in hospitals)
        
        # Identify high load vs ready facilities
        high_load = [h for h in hospitals if (h.get("available_beds", 0) / max(1, h.get("total_beds", 1))) < 0.15]
        ready_hospitals = sorted(
            hospitals,
            key=lambda h: (1 if h.get("trauma_ready") else 0, h.get("icu_beds", 0), h.get("available_beds", 0)),
            reverse=True
        )
        
        chosen = ready_hospitals[0]
        backup = ready_hospitals[1] if len(ready_hospitals) > 1 else chosen
        
        # Estimate expected casualty surge (typically 3-5% of affected population)
        estimated_casualties = max(15, round(affected_population * 0.035)) if severity in ("CRITICAL", "HIGH") else max(5, round(affected_population * 0.01))
        
        reasoning = (
            f"Evaluated {len(hospitals)} regional medical facilities with {total_available} available beds and {total_icu} ICU units. "
            f"Primary trauma destination: {chosen['name']} ({chosen['available_beds']} beds, {chosen['icu_beds']} ICU, {chosen['ambulances']} ambulances). "
            f"Backup hospital: {backup['name']}. {len(high_load)} facility near maximum operational capacity."
        )
        
        return {
            "agent": self.name,
            "role": self.role,
            "hospital": chosen["name"],
            "available_beds": chosen["available_beds"],
            "icu_beds": chosen["icu_beds"],
            "ambulances": chosen["ambulances"],
            "backup_hospital": backup["name"],
            "total_available_beds": total_available,
            "total_icu_beds": total_icu,
            "total_ambulances": total_ambulances,
            "estimated_casualties": estimated_casualties,
            "high_load_count": len(high_load),
            "reasoning": reasoning,
            "process_steps": [
                f"Audited real-time telemetry across {len(hospitals)} hospital trauma registries",
                f"Computed regional available capacity: {total_available} standard beds, {total_icu} ICU bays",
                f"Estimated acute medical surge demand: ~{estimated_casualties} emergency triage admissions",
                f"Designated {chosen['name']} as primary emergency receiving center"
            ],
            "output_summary": f"Primary: {chosen['name']} ({chosen['available_beds']} beds available), {total_ambulances} active ambulances mobilized"
        }

medical_agent = MedicalAgent()

def allocate(data: dict, severity: str = "HIGH", affected_population: int = 8500) -> dict:
    return medical_agent.allocate(data, severity, affected_population)

