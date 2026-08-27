def analyze(data: dict) -> dict:
    open_roads = [r for r in data["roads"] if r["status"] == "OPEN"]
    return {"safe_routes": open_roads, "affected_zones": [z["name"] for z in data["zones"] if z["severity"] in ("HIGH", "CRITICAL")], "reasoning": f"{len(open_roads)} open routes remain; blocked routes excluded from recommendations."}
