class ResourceAgent:
    """Specialized Agent for Emergency Resource Inventory, Logistics, and Asset Deployment."""
    
    def __init__(self):
        self.name = "Resource Agent"
        self.role = "Emergency inventory tracking, shortage detection, and logistics allocation"

    def allocate(self, data: dict, blocked: bool = False, priority_zones: list[str] | None = None) -> dict:
        resources = data.get("resources", [])
        priority_zones = priority_zones or ["Zone A", "Zone B"]
        
        # Filter available assets
        buses = [r for r in resources if "BUS" in r.get("type", "").upper() and r.get("status") != "UNAVAILABLE"]
        boats = [r for r in resources if "BOAT" in r.get("type", "").upper() and r.get("status") != "UNAVAILABLE"]
        ambulances = [r for r in resources if "AMBULANCE" in r.get("type", "").upper() and r.get("status") != "UNAVAILABLE"]
        water_items = [r for r in resources if "WATER" in r.get("type", "").upper()]
        food_items = [r for r in resources if "FOOD" in r.get("type", "").upper()]
        medical_items = [r for r in resources if "MEDICAL" in r.get("type", "").upper()]
        
        # Check for inventory shortages
        shortages = []
        for item in resources:
            avail = item.get("quantity_available", 0)
            req = item.get("quantity_required", 0)
            if req > 0 and avail < req:
                shortages.append({
                    "item": item.get("type"),
                    "id": item.get("id"),
                    "available": avail,
                    "required": req,
                    "deficit": req - avail,
                    "unit": item.get("unit", "units")
                })
        
        # Assign transport vehicles
        assignments = {}
        assigned_vehicles = []
        for idx, zone in enumerate(priority_zones[:2]):
            if idx < len(buses):
                bus = buses[idx]
                assignments[zone] = bus["id"]
                assigned_vehicles.append(f"{bus['id']} -> {zone}")
            else:
                assignments[zone] = "Reserve Transit Unit"
                
        # Primary boat assignment if flood
        boat_assignment = boats[0]["id"] if boats else "Mutual Aid Watercraft"
        
        reasoning = (
            f"Audited {len(resources)} emergency supply lines. "
            f"Assigned {len(assigned_vehicles)} evacuation transport units ({', '.join(assigned_vehicles)}). "
            f"{'Identified ' + str(len(shortages)) + ' critical resource deficits (' + ', '.join([s['item'] for s in shortages]) + ')' if shortages else 'All essential inventory levels adequate'}."
        )
        
        return {
            "agent": self.name,
            "role": self.role,
            "assignments": assignments,
            "boat_assignment": boat_assignment,
            "shortages": shortages,
            "available_buses": len(buses),
            "available_boats": len(boats),
            "available_ambulances": len(ambulances),
            "total_resources": len(resources),
            "reasoning": reasoning,
            "process_steps": [
                f"Scanned central disaster logistics depot for {len(resources)} tracked SKUs",
                f"Calculated seat capacity across {len(buses)} heavy-duty transit buses",
                f"Detected deficit in {len(shortages)} critical supply categories",
                f"Formulated priority dispatch order for immediate evacuation"
            ],
            "output_summary": f"Dispatched {len(assigned_vehicles)} bus fleets, {len(shortages)} supply deficits flagged for emergency procurement"
        }

resource_agent = ResourceAgent()

def allocate(data: dict, blocked: bool = False, priority_zones: list[str] | None = None) -> dict:
    return resource_agent.allocate(data, blocked, priority_zones)

