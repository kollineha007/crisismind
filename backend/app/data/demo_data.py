from copy import deepcopy

LOCATIONS = [
 {"id":"vijayawada","name":"Vijayawada","state":"Andhra Pradesh","latitude":16.5062,"longitude":80.6480},
 {"id":"hyderabad","name":"Hyderabad","state":"Telangana","latitude":17.3850,"longitude":78.4867},
 {"id":"visakhapatnam","name":"Visakhapatnam","state":"Andhra Pradesh","latitude":17.6868,"longitude":83.2185},
 {"id":"chennai","name":"Chennai","state":"Tamil Nadu","latitude":13.0827,"longitude":80.2707},
 {"id":"bengaluru","name":"Bengaluru","state":"Karnataka","latitude":12.9716,"longitude":77.5946},
 {"id":"mumbai","name":"Mumbai","state":"Maharashtra","latitude":19.0760,"longitude":72.8777},
 {"id":"delhi","name":"Delhi","state":"Delhi","latitude":28.6139,"longitude":77.2090},
]

ZONES = [
 {"name":"Zone A","population":2400,"severity":"HIGH","medical_risk":"HIGH","latitude":16.506,"longitude":80.641,"evacuation_status":"REQUIRED"},
 {"name":"Zone B","population":1900,"severity":"HIGH","medical_risk":"MEDIUM","latitude":16.512,"longitude":80.648,"evacuation_status":"REQUIRED"},
 {"name":"Zone C","population":1500,"severity":"MEDIUM","medical_risk":"MEDIUM","latitude":16.519,"longitude":80.635,"evacuation_status":"MONITOR"},
 {"name":"Zone D","population":1300,"severity":"MEDIUM","medical_risk":"LOW","latitude":16.499,"longitude":80.652,"evacuation_status":"MONITOR"},
 {"name":"Zone E","population":1400,"severity":"LOW","medical_risk":"LOW","latitude":16.525,"longitude":80.651,"evacuation_status":"MONITOR"},
]
ROADS = [
 {"id":"A-B","source":"Zone A","destination":"Zone B","distance":2.1,"status":"OPEN"},
 {"id":"A-C","source":"Zone A","destination":"Zone C","distance":3.8,"status":"OPEN"},
 {"id":"B-C","source":"Zone B","destination":"Zone C","distance":2.7,"status":"OPEN"},
 {"id":"B-D","source":"Zone B","destination":"Zone D","distance":3.2,"status":"AT_RISK"},
 {"id":"C-D","source":"Zone C","destination":"Zone D","distance":2.5,"status":"OPEN"},
 {"id":"C-E","source":"Zone C","destination":"Zone E","distance":3.1,"status":"OPEN"},
 {"id":"D-E","source":"Zone D","destination":"Zone E","distance":2.4,"status":"OPEN"},
 {"id":"A-D","source":"Zone A","destination":"Zone D","distance":4.4,"status":"OPEN"},
]
SHELTERS = [
 {"name":"Shelter A","zone":"Zone A","latitude":16.515,"longitude":80.625,"capacity":500,"occupancy":470,"accessibility":"Accessible","status":"OPEN"},
 {"name":"Shelter B","zone":"Zone B","latitude":16.530,"longitude":80.645,"capacity":1000,"occupancy":350,"accessibility":"Accessible","status":"OPEN"},
 {"name":"Shelter C","zone":"Zone C","latitude":16.538,"longitude":80.630,"capacity":900,"occupancy":300,"accessibility":"Accessible","status":"OPEN"},
 {"name":"Shelter D","zone":"Zone D","latitude":16.490,"longitude":80.660,"capacity":700,"occupancy":250,"accessibility":"Limited","status":"OPEN"},
 {"name":"Shelter E","zone":"Zone E","latitude":16.535,"longitude":80.665,"capacity":1200,"occupancy":800,"accessibility":"Accessible","status":"OPEN"},
]
HOSPITALS = [
 {"name":"Vijayawada General","latitude":16.508,"longitude":80.640,"total_beds":40,"available_beds":8,"icu_beds":2,"ambulances":1,"status":"OPEN"},
 {"name":"Krishna Medical Center","latitude":16.520,"longitude":80.650,"total_beds":60,"available_beds":18,"icu_beds":5,"ambulances":2,"status":"OPEN"},
 {"name":"City Care Hospital","latitude":16.495,"longitude":80.635,"total_beds":30,"available_beds":6,"icu_beds":1,"ambulances":1,"status":"OPEN"},
 {"name":"Amaravati Emergency","latitude":16.535,"longitude":80.655,"total_beds":45,"available_beds":12,"icu_beds":3,"ambulances":2,"status":"OPEN"},
]
RESOURCES = [
 {"id":"Bus 01","type":"BUS","location":"Zone B","capacity":50,"status":"AVAILABLE"}, {"id":"Bus 02","type":"BUS","location":"Zone C","capacity":50,"status":"AVAILABLE"}, {"id":"Bus 03","type":"BUS","location":"Zone D","capacity":40,"status":"AVAILABLE"}, {"id":"Bus 04","type":"BUS","location":"Zone E","capacity":50,"status":"AVAILABLE"}, {"id":"Ambulance 01","type":"AMBULANCE","location":"Zone B","capacity":2,"status":"AVAILABLE"}, {"id":"Ambulance 02","type":"AMBULANCE","location":"Zone C","capacity":2,"status":"AVAILABLE"}, {"id":"Rescue 01","type":"RESCUE VEHICLE","location":"Zone D","capacity":8,"status":"AVAILABLE"}, {"id":"Rescue Team 01","type":"RESCUE TEAM","location":"Zone B","capacity":6,"status":"AVAILABLE"}, {"id":"Boat 01","type":"BOAT","location":"Zone A","capacity":12,"status":"AVAILABLE"}, {"id":"Volunteers 01","type":"VOLUNTEERS","location":"Zone C","capacity":20,"status":"AVAILABLE"},
]

def snapshot(location_id="vijayawada"):
	location=next((item for item in LOCATIONS if item["id"]==location_id),LOCATIONS[0])
	data={"zones": deepcopy(ZONES), "roads": deepcopy(ROADS), "shelters": deepcopy(SHELTERS), "hospitals": deepcopy(HOSPITALS), "resources": deepcopy(RESOURCES)}
	lat_delta=location["latitude"]-LOCATIONS[0]["latitude"]; lon_delta=location["longitude"]-LOCATIONS[0]["longitude"]
	for group in ("zones","shelters","hospitals"):
		for item in data[group]: item["latitude"]+=lat_delta; item["longitude"]+=lon_delta
	return data
