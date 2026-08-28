from copy import deepcopy

LOCATIONS = [
    {
        "id": "vijayawada",
        "name": "Vijayawada",
        "state": "Andhra Pradesh",
        "latitude": 16.5062,
        "longitude": 80.6480,
        "default_crisis": "Flood",
        "severity": "HIGH",
        "affected_population": 12500,
        "water_level": 2.8,
        "blocked_roads": 3,
        "risk_summary": "Krishna River overflow causing severe inundation across low-lying residential sectors."
    },
    {
        "id": "hyderabad",
        "name": "Hyderabad",
        "state": "Telangana",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "default_crisis": "Heavy Rain & Waterlogging",
        "severity": "MEDIUM",
        "affected_population": 4200,
        "water_level": 1.4,
        "blocked_roads": 1,
        "risk_summary": "Flash cloudburst inundating arterial underpasses and drainage bottlenecks."
    },
    {
        "id": "delhi",
        "name": "Delhi",
        "state": "National Capital Territory",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "default_crisis": "Heatwave & Air Quality Crisis",
        "severity": "LOW",
        "affected_population": 1800,
        "water_level": 0.0,
        "blocked_roads": 0,
        "risk_summary": "Severe thermal stress and AQI surge requiring hydration centers and cooling shelters."
    },
    {
        "id": "mumbai",
        "name": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "default_crisis": "Coastal Cyclone & High Tide Inundation",
        "severity": "CRITICAL",
        "affected_population": 16400,
        "water_level": 3.2,
        "blocked_roads": 4,
        "risk_summary": "Storm surge combined with 4.5m high tide threatening coastal slums and transit hubs."
    },
    {
        "id": "visakhapatnam",
        "name": "Visakhapatnam",
        "state": "Andhra Pradesh",
        "latitude": 17.6868,
        "longitude": 83.2185,
        "default_crisis": "Cyclone Landfall Warning",
        "severity": "HIGH",
        "affected_population": 8200,
        "water_level": 2.1,
        "blocked_roads": 2,
        "risk_summary": "Gale winds and tidal surge warning for beachfront fishing settlements."
    },
    {
        "id": "chennai",
        "name": "Chennai",
        "state": "Tamil Nadu",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "default_crisis": "Monsoon Inundation",
        "severity": "HIGH",
        "affected_population": 9500,
        "water_level": 2.2,
        "blocked_roads": 2,
        "risk_summary": "Adyar basin overflow flooding low-lying residential belts."
    },
    {
        "id": "bengaluru",
        "name": "Bengaluru",
        "state": "Karnataka",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "default_crisis": "Flash Flooding",
        "severity": "MEDIUM",
        "affected_population": 3800,
        "water_level": 1.2,
        "blocked_roads": 1,
        "risk_summary": "Storm drain breach causing waterlogging in major tech corridor arteries."
    }
]

LOCATION_DATASETS = {
    "vijayawada": {
        "zones": [
            {"name": "Zone A (Krishnalanka)", "population": 4200, "severity": "CRITICAL", "medical_risk": "HIGH", "latitude": 16.502, "longitude": 80.638, "evacuation_status": "URGENT_EVACUATION"},
            {"name": "Zone B (Bhavanipuram)", "population": 3600, "severity": "HIGH", "medical_risk": "HIGH", "latitude": 16.518, "longitude": 80.612, "evacuation_status": "REQUIRED"},
            {"name": "Zone C (Governorpet)", "population": 2500, "severity": "MEDIUM", "medical_risk": "MEDIUM", "latitude": 16.511, "longitude": 80.648, "evacuation_status": "MONITOR"},
            {"name": "Zone D (Gunadala)", "population": 1400, "severity": "MEDIUM", "medical_risk": "LOW", "latitude": 16.526, "longitude": 80.665, "evacuation_status": "MONITOR"},
            {"name": "Zone E (Autonagar Safe Zone)", "population": 800, "severity": "LOW", "medical_risk": "LOW", "latitude": 16.495, "longitude": 80.680, "evacuation_status": "SAFE_HAVEN"}
        ],
        "roads": [
            {"id": "Route A-B (NH-65 Bypass)", "source": "Zone A (Krishnalanka)", "destination": "Zone B (Bhavanipuram)", "distance": 2.4, "status": "BLOCKED", "risk_level": "CRITICAL"},
            {"id": "Route A-C (MG Road Flyover)", "source": "Zone A (Krishnalanka)", "destination": "Zone C (Governorpet)", "distance": 3.1, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Route B-C (Canal Causeway)", "source": "Zone B (Bhavanipuram)", "destination": "Zone C (Governorpet)", "distance": 2.8, "status": "AT_RISK", "risk_level": "MEDIUM"},
            {"id": "Route B-D (Inner Ring Road)", "source": "Zone B (Bhavanipuram)", "destination": "Zone D (Gunadala)", "distance": 4.5, "status": "BLOCKED", "risk_level": "HIGH"},
            {"id": "Route C-D (Eluru Road Highline)", "source": "Zone C (Governorpet)", "destination": "Zone D (Gunadala)", "distance": 2.2, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Route C-E (Bandar Road Highway)", "source": "Zone C (Governorpet)", "destination": "Zone E (Autonagar Safe Zone)", "distance": 4.8, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Route D-E (Eastern Link Road)", "source": "Zone D (Gunadala)", "destination": "Zone E (Autonagar Safe Zone)", "distance": 3.6, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Route A-E (Old Riverbed Link)", "source": "Zone A (Krishnalanka)", "destination": "Zone E (Autonagar Safe Zone)", "distance": 5.2, "status": "BLOCKED", "risk_level": "CRITICAL"}
        ],
        "shelters": [
            {"name": "Indira Gandhi Municipal Stadium", "zone": "Zone C (Governorpet)", "latitude": 16.508, "longitude": 80.642, "capacity": 2500, "occupancy": 1900, "accessibility": "High-Clearance Access Only", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Autonagar Community Center", "zone": "Zone E (Autonagar Safe Zone)", "latitude": 16.494, "longitude": 80.678, "capacity": 3000, "occupancy": 650, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Gunadala Mary Matha Shrine Hall", "zone": "Zone D (Gunadala)", "latitude": 16.529, "longitude": 80.662, "capacity": 1500, "occupancy": 820, "accessibility": "Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Bhavanipuram ZP High School", "zone": "Zone B (Bhavanipuram)", "latitude": 16.516, "longitude": 80.615, "capacity": 800, "occupancy": 760, "accessibility": "Flood Warning", "status": "AT_CAPACITY", "safety_level": "MEDIUM"},
            {"name": "Krishnalanka Relief Tent City", "zone": "Zone A (Krishnalanka)", "latitude": 16.501, "longitude": 80.635, "capacity": 600, "occupancy": 580, "accessibility": "Submerged Entrance", "status": "UNSAFE", "safety_level": "LOW"}
        ],
        "hospitals": [
            {"name": "Government General Hospital (GGH Vijayawada)", "latitude": 16.509, "longitude": 80.645, "total_beds": 650, "available_beds": 42, "icu_beds": 8, "ambulances": 5, "status": "HIGH_LOAD", "trauma_ready": True},
            {"name": "Andhra Hospitals Heart & Emergency", "latitude": 16.515, "longitude": 80.639, "total_beds": 350, "available_beds": 65, "icu_beds": 14, "ambulances": 4, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "Ramesh Multi-Specialty Hospital", "latitude": 16.498, "longitude": 80.655, "total_beds": 400, "available_beds": 92, "icu_beds": 18, "ambulances": 6, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "Ayush Emergency Trauma Center", "latitude": 16.528, "longitude": 80.660, "total_beds": 200, "available_beds": 28, "icu_beds": 4, "ambulances": 3, "status": "HIGH_LOAD", "trauma_ready": False}
        ],
        "resources": [
            {"id": "NDRF Boat Squad 01", "type": "RESCUE BOATS", "unit": "Boats", "quantity_available": 6, "quantity_required": 10, "location": "Zone A (Krishnalanka)", "capacity": 72, "status": "ASSIGNED", "assigned_zone": "Zone A (Krishnalanka)"},
            {"id": "State Disaster Bus Fleet 01", "type": "EMERGENCY BUSES", "unit": "Buses", "quantity_available": 14, "quantity_required": 18, "location": "Zone C (Governorpet)", "capacity": 700, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "Emergency Potable Water Tankers", "type": "POTABLE WATER", "unit": "Liters (x1000)", "quantity_available": 4200, "quantity_required": 7500, "location": "Zone E (Autonagar Safe Zone)", "capacity": 4200, "status": "CRITICAL", "assigned_zone": None},
            {"id": "Dry Ration & Food Relief Packs", "type": "FOOD PACKS", "unit": "Ration Kits", "quantity_available": 5600, "quantity_required": 8000, "location": "Zone C (Governorpet)", "capacity": 5600, "status": "LOW", "assigned_zone": None},
            {"id": "Mobile ICU Ambulance Unit", "type": "AMBULANCES", "unit": "Vehicles", "quantity_available": 8, "quantity_required": 12, "location": "GGH Hospital Base", "capacity": 16, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "First Aid & Trauma Medical Kits", "type": "MEDICAL KITS", "unit": "Kits", "quantity_available": 450, "quantity_required": 600, "location": "Ramesh Hospital Depot", "capacity": 450, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "State Fire & Heavy Rescue Team", "type": "RESCUE VEHICLES", "unit": "Trucks", "quantity_available": 4, "quantity_required": 6, "location": "Autonagar Depot", "capacity": 32, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "Red Cross Volunteer Brigade", "type": "VOLUNTEERS", "unit": "Personnel", "quantity_available": 65, "quantity_required": 100, "location": "Municipal Stadium", "capacity": 65, "status": "ASSIGNED", "assigned_zone": "Zone C (Governorpet)"}
        ]
    },
    "hyderabad": {
        "zones": [
            {"name": "Zone A (Moosi Riverbank)", "population": 1600, "severity": "HIGH", "medical_risk": "MEDIUM", "latitude": 17.375, "longitude": 78.474, "evacuation_status": "REQUIRED"},
            {"name": "Zone B (Khairatabad Lowland)", "population": 1200, "severity": "MEDIUM", "medical_risk": "MEDIUM", "latitude": 17.412, "longitude": 78.461, "evacuation_status": "MONITOR"},
            {"name": "Zone C (Secunderabad Rail Hub)", "population": 800, "severity": "LOW", "medical_risk": "LOW", "latitude": 17.439, "longitude": 78.498, "evacuation_status": "MONITOR"},
            {"name": "Zone D (Banjara Hills Safe Zone)", "population": 600, "severity": "LOW", "medical_risk": "LOW", "latitude": 17.415, "longitude": 78.435, "evacuation_status": "SAFE_HAVEN"}
        ],
        "roads": [
            {"id": "Route 1 (PVNR Expressway)", "source": "Zone A (Moosi Riverbank)", "destination": "Zone D (Banjara Hills Safe Zone)", "distance": 5.4, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Route 2 (Moosi Flood Causeway)", "source": "Zone A (Moosi Riverbank)", "destination": "Zone B (Khairatabad Lowland)", "distance": 3.2, "status": "BLOCKED", "risk_level": "HIGH"},
            {"id": "Route 3 (Necklace Road)", "source": "Zone B (Khairatabad Lowland)", "destination": "Zone C (Secunderabad Rail Hub)", "distance": 4.1, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Route 4 (Raj Bhavan High Road)", "source": "Zone B (Khairatabad Lowland)", "destination": "Zone D (Banjara Hills Safe Zone)", "distance": 2.9, "status": "OPEN", "risk_level": "LOW"}
        ],
        "shelters": [
            {"name": "L.B. Stadium Indoor Complex", "zone": "Zone B (Khairatabad Lowland)", "latitude": 17.401, "longitude": 78.475, "capacity": 2000, "occupancy": 650, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Jubilee Hills Community Shelter", "zone": "Zone D (Banjara Hills Safe Zone)", "latitude": 17.428, "longitude": 78.412, "capacity": 1500, "occupancy": 320, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Secunderabad YMCA Shelter", "zone": "Zone C (Secunderabad Rail Hub)", "latitude": 17.442, "longitude": 78.495, "capacity": 1000, "occupancy": 410, "accessibility": "Accessible", "status": "OPEN", "safety_level": "HIGH"}
        ],
        "hospitals": [
            {"name": "Osmania General Hospital", "latitude": 17.378, "longitude": 78.473, "total_beds": 800, "available_beds": 140, "icu_beds": 22, "ambulances": 8, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "NIMS Hospital Punjagutta", "latitude": 17.422, "longitude": 78.452, "total_beds": 650, "available_beds": 115, "icu_beds": 28, "ambulances": 6, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "Gandhi Hospital Secunderabad", "latitude": 17.425, "longitude": 78.503, "total_beds": 750, "available_beds": 190, "icu_beds": 35, "ambulances": 7, "status": "OPERATIONAL", "trauma_ready": True}
        ],
        "resources": [
            {"id": "GHMC Drainage Pumpset Fleet", "type": "RESCUE VEHICLES", "unit": "Pump Trucks", "quantity_available": 12, "quantity_required": 10, "location": "Khairatabad Depot", "capacity": 48, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "Telangana RTC Emergency Shuttles", "type": "EMERGENCY BUSES", "unit": "Buses", "quantity_available": 20, "quantity_required": 15, "location": "Secunderabad Depot", "capacity": 1000, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "Mission Bhagiratha Water Tanks", "type": "POTABLE WATER", "unit": "Liters (x1000)", "quantity_available": 8500, "quantity_required": 5000, "location": "Banjara Hills Reservoir", "capacity": 8500, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "Red Cross Emergency First Aid Packs", "type": "MEDICAL KITS", "unit": "Kits", "quantity_available": 600, "quantity_required": 400, "location": "NIMS Logistics Unit", "capacity": 600, "status": "AVAILABLE", "assigned_zone": None}
        ]
    },
    "delhi": {
        "zones": [
            {"name": "Zone A (Yamuna Floodplain Slums)", "population": 850, "severity": "MEDIUM", "medical_risk": "MEDIUM", "latitude": 28.642, "longitude": 77.265, "evacuation_status": "MONITOR"},
            {"name": "Zone B (Old Delhi Walled City)", "population": 550, "severity": "LOW", "medical_risk": "LOW", "latitude": 28.656, "longitude": 77.230, "evacuation_status": "MONITOR"},
            {"name": "Zone C (Chanakyapuri Safe Sector)", "population": 400, "severity": "LOW", "medical_risk": "LOW", "latitude": 28.598, "longitude": 77.185, "evacuation_status": "SAFE_HAVEN"}
        ],
        "roads": [
            {"id": "Ring Road Outer Corridor", "source": "Zone A (Yamuna Floodplain Slums)", "destination": "Zone C (Chanakyapuri Safe Sector)", "distance": 9.2, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Vikas Marg Expressway", "source": "Zone A (Yamuna Floodplain Slums)", "destination": "Zone B (Old Delhi Walled City)", "distance": 4.5, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Ashoka Road High Arterial", "source": "Zone B (Old Delhi Walled City)", "destination": "Zone C (Chanakyapuri Safe Sector)", "distance": 5.8, "status": "OPEN", "risk_level": "LOW"}
        ],
        "shelters": [
            {"name": "Thyagaraj Air-Cooled Relief Center", "zone": "Zone C (Chanakyapuri Safe Sector)", "latitude": 28.578, "longitude": 77.218, "capacity": 3000, "occupancy": 320, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Yamuna Sports Complex Shelter", "zone": "Zone A (Yamuna Floodplain Slums)", "latitude": 28.655, "longitude": 77.305, "capacity": 2500, "occupancy": 480, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"}
        ],
        "hospitals": [
            {"name": "AIIMS New Delhi Trauma Center", "latitude": 28.567, "longitude": 77.210, "total_beds": 1200, "available_beds": 240, "icu_beds": 48, "ambulances": 15, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "Safdarjung Emergency Hospital", "latitude": 28.570, "longitude": 77.207, "total_beds": 950, "available_beds": 180, "icu_beds": 36, "ambulances": 12, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "LNJP Hospital Daryaganj", "latitude": 28.636, "longitude": 77.241, "total_beds": 800, "available_beds": 160, "icu_beds": 25, "ambulances": 10, "status": "OPERATIONAL", "trauma_ready": True}
        ],
        "resources": [
            {"id": "Mobile ORS & Hydration Units", "type": "POTABLE WATER", "unit": "Hydration Packs", "quantity_available": 12000, "quantity_required": 4000, "location": "Central Delhi Depot", "capacity": 12000, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "Heatstroke Emergency Ambulances", "type": "AMBULANCES", "unit": "Vehicles", "quantity_available": 18, "quantity_required": 8, "location": "AIIMS Base", "capacity": 36, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "DTC Air-Conditioned Evac Buses", "type": "EMERGENCY BUSES", "unit": "Buses", "quantity_available": 25, "quantity_required": 10, "location": "Millennium Park Depot", "capacity": 1250, "status": "AVAILABLE", "assigned_zone": None}
        ]
    },
    "mumbai": {
        "zones": [
            {"name": "Zone A (Colaba & Marine Drive)", "population": 5800, "severity": "CRITICAL", "medical_risk": "HIGH", "latitude": 18.915, "longitude": 72.825, "evacuation_status": "URGENT_EVACUATION"},
            {"name": "Zone B (Kurla & Mithi River Basin)", "population": 6200, "severity": "CRITICAL", "medical_risk": "HIGH", "latitude": 19.068, "longitude": 72.885, "evacuation_status": "URGENT_EVACUATION"},
            {"name": "Zone C (Dadar Lowland)", "population": 3100, "severity": "HIGH", "medical_risk": "MEDIUM", "latitude": 19.018, "longitude": 72.842, "evacuation_status": "REQUIRED"},
            {"name": "Zone D (Powai Highland Safe Zone)", "population": 1300, "severity": "LOW", "medical_risk": "LOW", "latitude": 19.120, "longitude": 72.905, "evacuation_status": "SAFE_HAVEN"}
        ],
        "roads": [
            {"id": "Western Express Highway Overpass", "source": "Zone C (Dadar Lowland)", "destination": "Zone D (Powai Highland Safe Zone)", "distance": 8.6, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Mithi River Causeway", "source": "Zone B (Kurla & Mithi River Basin)", "destination": "Zone D (Powai Highland Safe Zone)", "distance": 4.8, "status": "BLOCKED", "risk_level": "CRITICAL"},
            {"id": "Eastern Freeway Elevated", "source": "Zone A (Colaba & Marine Drive)", "destination": "Zone D (Powai Highland Safe Zone)", "distance": 14.2, "status": "OPEN", "risk_level": "LOW"},
            {"id": "S.V. Road Lowline", "source": "Zone B (Kurla & Mithi River Basin)", "destination": "Zone C (Dadar Lowland)", "distance": 5.1, "status": "BLOCKED", "risk_level": "HIGH"}
        ],
        "shelters": [
            {"name": "Bandra Kurla Complex Center", "zone": "Zone B (Kurla & Mithi River Basin)", "latitude": 19.060, "longitude": 72.865, "capacity": 4500, "occupancy": 3800, "accessibility": "Flood Warning", "status": "AT_CAPACITY", "safety_level": "MEDIUM"},
            {"name": "IIT Bombay Indoor Sports Stadium", "zone": "Zone D (Powai Highland Safe Zone)", "latitude": 19.133, "longitude": 72.915, "capacity": 5000, "occupancy": 1100, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Wankhede Concourse Shelter", "zone": "Zone A (Colaba & Marine Drive)", "latitude": 18.938, "longitude": 72.825, "capacity": 3000, "occupancy": 2400, "accessibility": "Storm Warning", "status": "OPEN", "safety_level": "MEDIUM"}
        ],
        "hospitals": [
            {"name": "KEM Hospital Parel", "latitude": 19.002, "longitude": 72.842, "total_beds": 900, "available_beds": 52, "icu_beds": 12, "ambulances": 6, "status": "HIGH_LOAD", "trauma_ready": True},
            {"name": "Lilavati Multi-Specialty Bandra", "latitude": 19.052, "longitude": 72.828, "total_beds": 450, "available_beds": 88, "icu_beds": 20, "ambulances": 8, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "Hiranandani Hospital Powai", "latitude": 19.118, "longitude": 72.909, "total_beds": 350, "available_beds": 95, "icu_beds": 18, "ambulances": 7, "status": "OPERATIONAL", "trauma_ready": True}
        ],
        "resources": [
            {"id": "Indian Navy Sea King Rescue Unit", "type": "RESCUE BOATS", "unit": "Helo / Boats", "quantity_available": 10, "quantity_required": 14, "location": "Colaba Naval Base", "capacity": 120, "status": "ASSIGNED", "assigned_zone": "Zone A (Colaba & Marine Drive)"},
            {"id": "BEST Double Decker Evacuation Fleet", "type": "EMERGENCY BUSES", "unit": "Buses", "quantity_available": 30, "quantity_required": 40, "location": "Dadar Depot", "capacity": 2100, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "Emergency Drinking Water Packets", "type": "POTABLE WATER", "unit": "Liters (x1000)", "quantity_available": 5400, "quantity_required": 9000, "location": "Powai Hub", "capacity": 5400, "status": "CRITICAL", "assigned_zone": None}
        ]
    },
    "visakhapatnam": {
        "zones": [
            {"name": "Zone A (RK Beach & Fishing Harbor)", "population": 3400, "severity": "HIGH", "medical_risk": "HIGH", "latitude": 17.712, "longitude": 83.318, "evacuation_status": "URGENT_EVACUATION"},
            {"name": "Zone B (Kurupam Lowlands)", "population": 2600, "severity": "HIGH", "medical_risk": "MEDIUM", "latitude": 17.698, "longitude": 83.295, "evacuation_status": "REQUIRED"},
            {"name": "Zone C (Dwaraka Nagar Transit Hub)", "population": 1400, "severity": "MEDIUM", "medical_risk": "LOW", "latitude": 17.725, "longitude": 83.305, "evacuation_status": "MONITOR"},
            {"name": "Zone D (Kailasagiri Highland Safe Zone)", "population": 800, "severity": "LOW", "medical_risk": "LOW", "latitude": 17.750, "longitude": 83.342, "evacuation_status": "SAFE_HAVEN"}
        ],
        "roads": [
            {"id": "Beach Road Coastal Highway", "source": "Zone A (RK Beach & Fishing Harbor)", "destination": "Zone D (Kailasagiri Highland Safe Zone)", "distance": 6.8, "status": "BLOCKED", "risk_level": "CRITICAL"},
            {"id": "Waltair Main Arterial", "source": "Zone A (RK Beach & Fishing Harbor)", "destination": "Zone C (Dwaraka Nagar Transit Hub)", "distance": 3.4, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Port Road Flyover", "source": "Zone B (Kurupam Lowlands)", "destination": "Zone C (Dwaraka Nagar Transit Hub)", "distance": 4.1, "status": "BLOCKED", "risk_level": "HIGH"},
            {"id": "BRTS Northern Corridor", "source": "Zone C (Dwaraka Nagar Transit Hub)", "destination": "Zone D (Kailasagiri Highland Safe Zone)", "distance": 5.2, "status": "OPEN", "risk_level": "LOW"}
        ],
        "shelters": [
            {"name": "Swarna Bharathi Indoor Stadium", "zone": "Zone C (Dwaraka Nagar Transit Hub)", "latitude": 17.728, "longitude": 83.310, "capacity": 2800, "occupancy": 1200, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Andhra University Gymnasium Shelter", "zone": "Zone D (Kailasagiri Highland Safe Zone)", "latitude": 17.732, "longitude": 83.325, "capacity": 2200, "occupancy": 450, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Fisheries Training Institute Hall", "zone": "Zone A (RK Beach & Fishing Harbor)", "latitude": 17.705, "longitude": 83.308, "capacity": 900, "occupancy": 810, "accessibility": "Gale Warning", "status": "AT_CAPACITY", "safety_level": "MEDIUM"}
        ],
        "hospitals": [
            {"name": "King George Hospital (KGH Vizag)", "latitude": 17.708, "longitude": 83.303, "total_beds": 750, "available_beds": 84, "icu_beds": 18, "ambulances": 8, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "Care Multi-Specialty Ramnagar", "latitude": 17.720, "longitude": 83.312, "total_beds": 350, "available_beds": 62, "icu_beds": 12, "ambulances": 5, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "Apollo Emergency Hospital Arilova", "latitude": 17.765, "longitude": 83.332, "total_beds": 300, "available_beds": 75, "icu_beds": 16, "ambulances": 6, "status": "OPERATIONAL", "trauma_ready": True}
        ],
        "resources": [
            {"id": "Eastern Naval Command Inflatable Crafts", "type": "RESCUE BOATS", "unit": "Boats", "quantity_available": 8, "quantity_required": 12, "location": "Naval Dockyard Base", "capacity": 96, "status": "ASSIGNED", "assigned_zone": "Zone A (RK Beach & Fishing Harbor)"},
            {"id": "APSRTC Cyclone Transit Fleet", "type": "EMERGENCY BUSES", "unit": "Buses", "quantity_available": 16, "quantity_required": 20, "location": "Dwaraka Bus Complex", "capacity": 800, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "Vizag Municipal Potable Water Tanks", "type": "POTABLE WATER", "unit": "Liters (x1000)", "quantity_available": 6000, "quantity_required": 7500, "location": "Maddilapalem Depot", "capacity": 6000, "status": "LOW", "assigned_zone": None},
            {"id": "Emergency Cyclone Medical Kits", "type": "MEDICAL KITS", "unit": "Kits", "quantity_available": 350, "quantity_required": 500, "location": "KGH Depot", "capacity": 350, "status": "AVAILABLE", "assigned_zone": None}
        ]
    },
    "chennai": {
        "zones": [
            {"name": "Zone A (Velachery Low Basin)", "population": 4100, "severity": "HIGH", "medical_risk": "HIGH", "latitude": 12.981, "longitude": 80.218, "evacuation_status": "URGENT_EVACUATION"},
            {"name": "Zone B (Adyar Riverbank Colony)", "population": 3200, "severity": "HIGH", "medical_risk": "MEDIUM", "latitude": 13.006, "longitude": 80.257, "evacuation_status": "REQUIRED"},
            {"name": "Zone C (T. Nagar Commercial Sector)", "population": 1600, "severity": "MEDIUM", "medical_risk": "LOW", "latitude": 13.041, "longitude": 80.233, "evacuation_status": "MONITOR"},
            {"name": "Zone D (Guindy Highland Safe Zone)", "population": 600, "severity": "LOW", "medical_risk": "LOW", "latitude": 13.007, "longitude": 80.211, "evacuation_status": "SAFE_HAVEN"}
        ],
        "roads": [
            {"id": "Velachery Main Bypass", "source": "Zone A (Velachery Low Basin)", "destination": "Zone D (Guindy Highland Safe Zone)", "distance": 4.5, "status": "BLOCKED", "risk_level": "CRITICAL"},
            {"id": "Inner Ring Road Highline", "source": "Zone A (Velachery Low Basin)", "destination": "Zone C (T. Nagar Commercial Sector)", "distance": 6.2, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Adyar Bridge Arterial", "source": "Zone B (Adyar Riverbank Colony)", "destination": "Zone C (T. Nagar Commercial Sector)", "distance": 3.8, "status": "BLOCKED", "risk_level": "HIGH"},
            {"id": "Mount Road (Anna Salai)", "source": "Zone C (T. Nagar Commercial Sector)", "destination": "Zone D (Guindy Highland Safe Zone)", "distance": 5.1, "status": "OPEN", "risk_level": "LOW"}
        ],
        "shelters": [
            {"name": "Jawaharlal Nehru Indoor Stadium", "zone": "Zone C (T. Nagar Commercial Sector)", "latitude": 13.084, "longitude": 80.278, "capacity": 3500, "occupancy": 1800, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Anna University Gymnasium Center", "zone": "Zone D (Guindy Highland Safe Zone)", "latitude": 13.013, "longitude": 80.236, "capacity": 2500, "occupancy": 620, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Velachery Community Hall", "zone": "Zone A (Velachery Low Basin)", "latitude": 12.978, "longitude": 80.221, "capacity": 1000, "occupancy": 920, "accessibility": "Waterlogging Notice", "status": "AT_CAPACITY", "safety_level": "MEDIUM"}
        ],
        "hospitals": [
            {"name": "Rajiv Gandhi Govt General Hospital (RGGGH)", "latitude": 13.081, "longitude": 80.277, "total_beds": 1000, "available_beds": 110, "icu_beds": 26, "ambulances": 10, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "Apollo Hospitals Greams Road", "latitude": 13.060, "longitude": 80.252, "total_beds": 550, "available_beds": 72, "icu_beds": 22, "ambulances": 8, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "KMC Hospital Kilpauk", "latitude": 13.079, "longitude": 80.243, "total_beds": 450, "available_beds": 58, "icu_beds": 14, "ambulances": 6, "status": "OPERATIONAL", "trauma_ready": True}
        ],
        "resources": [
            {"id": "Tamil Nadu SDRF Zodiac Boats", "type": "RESCUE BOATS", "unit": "Boats", "quantity_available": 10, "quantity_required": 15, "location": "Adyar Boat Depot", "capacity": 120, "status": "ASSIGNED", "assigned_zone": "Zone A (Velachery Low Basin)"},
            {"id": "MTC Evacuation Bus Convoy", "type": "EMERGENCY BUSES", "unit": "Buses", "quantity_available": 22, "quantity_required": 28, "location": "T. Nagar Bus Depot", "capacity": 1100, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "Chennai Metro Water Emergency Tankers", "type": "POTABLE WATER", "unit": "Liters (x1000)", "quantity_available": 7200, "quantity_required": 9500, "location": "Kilpauk Water Works", "capacity": 7200, "status": "LOW", "assigned_zone": None}
        ]
    },
    "bengaluru": {
        "zones": [
            {"name": "Zone A (Bellandur Lake Catchment)", "population": 1900, "severity": "MEDIUM", "medical_risk": "MEDIUM", "latitude": 12.935, "longitude": 77.674, "evacuation_status": "REQUIRED"},
            {"name": "Zone B (Silk Board Lowland Junction)", "population": 1200, "severity": "MEDIUM", "medical_risk": "LOW", "latitude": 12.917, "longitude": 77.623, "evacuation_status": "MONITOR"},
            {"name": "Zone C (Indiranagar Urban Sector)", "population": 700, "severity": "LOW", "medical_risk": "LOW", "latitude": 12.978, "longitude": 77.640, "evacuation_status": "MONITOR"}
        ],
        "roads": [
            {"id": "Outer Ring Road (ORR Tech Arterial)", "source": "Zone A (Bellandur Lake Catchment)", "destination": "Zone C (Indiranagar Urban Sector)", "distance": 6.8, "status": "BLOCKED", "risk_level": "HIGH"},
            {"id": "Hosur Elevated Expressway", "source": "Zone B (Silk Board Lowland Junction)", "destination": "Zone C (Indiranagar Urban Sector)", "distance": 7.4, "status": "OPEN", "risk_level": "LOW"},
            {"id": "Old Airport Road Highline", "source": "Zone A (Bellandur Lake Catchment)", "destination": "Zone C (Indiranagar Urban Sector)", "distance": 5.2, "status": "OPEN", "risk_level": "LOW"}
        ],
        "shelters": [
            {"name": "Koramangala Indoor Sports Complex", "zone": "Zone B (Silk Board Lowland Junction)", "latitude": 12.934, "longitude": 77.620, "capacity": 2200, "occupancy": 550, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"},
            {"name": "Kanteerava Stadium Shelter", "zone": "Zone C (Indiranagar Urban Sector)", "latitude": 12.969, "longitude": 77.592, "capacity": 3500, "occupancy": 400, "accessibility": "Fully Accessible", "status": "OPEN", "safety_level": "HIGH"}
        ],
        "hospitals": [
            {"name": "Victoria General Hospital", "latitude": 12.964, "longitude": 77.575, "total_beds": 800, "available_beds": 160, "icu_beds": 28, "ambulances": 10, "status": "OPERATIONAL", "trauma_ready": True},
            {"name": "Manipal Multi-Specialty Old Airport Rd", "latitude": 12.958, "longitude": 77.650, "total_beds": 500, "available_beds": 95, "icu_beds": 20, "ambulances": 8, "status": "OPERATIONAL", "trauma_ready": True}
        ],
        "resources": [
            {"id": "BBMP Flood Inundation Dewatering Fleet", "type": "RESCUE VEHICLES", "unit": "Pump Units", "quantity_available": 14, "quantity_required": 10, "location": "Bellandur Depot", "capacity": 56, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "BMTC Flood Relief Buses", "type": "EMERGENCY BUSES", "unit": "Buses", "quantity_available": 18, "quantity_required": 12, "location": "Indiranagar Depot", "capacity": 900, "status": "AVAILABLE", "assigned_zone": None},
            {"id": "BWSSB Clean Drinking Water Tankers", "type": "POTABLE WATER", "unit": "Liters (x1000)", "quantity_available": 9000, "quantity_required": 6000, "location": "Koramangala Reservoir", "capacity": 9000, "status": "AVAILABLE", "assigned_zone": None}
        ]
    }
}

def snapshot(location_id="vijayawada") -> dict:
    loc_id = location_id.lower() if location_id else "vijayawada"
    matched_loc = next((item for item in LOCATIONS if item["id"] == loc_id), LOCATIONS[0])
    
    if loc_id in LOCATION_DATASETS:
        dataset = deepcopy(LOCATION_DATASETS[loc_id])
    else:
        # Generate synthetic dataset scaled from Vijayawada relative to coordinates
        dataset = deepcopy(LOCATION_DATASETS["vijayawada"])
        lat_delta = matched_loc["latitude"] - LOCATIONS[0]["latitude"]
        lon_delta = matched_loc["longitude"] - LOCATIONS[0]["longitude"]
        scale = 0.7
        
        for group in ("zones", "shelters", "hospitals"):
            for item in dataset[group]:
                item["latitude"] += lat_delta
                item["longitude"] += lon_delta
                
        for zone in dataset["zones"]:
            zone["population"] = round(zone["population"] * scale)
            zone["severity"] = matched_loc.get("severity", "MEDIUM")
            zone["name"] = zone["name"].split(" (")[0] + f" ({matched_loc['name']} Sector)"
            
        for shelter in dataset["shelters"]:
            shelter["capacity"] = round(shelter["capacity"] * scale)
            shelter["occupancy"] = min(round(shelter["occupancy"] * scale), shelter["capacity"])
            
        for hospital in dataset["hospitals"]:
            hospital["total_beds"] = round(hospital["total_beds"] * scale)
            hospital["available_beds"] = min(round(hospital["available_beds"] * scale), hospital["total_beds"])

    return dataset

