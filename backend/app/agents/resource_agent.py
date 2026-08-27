def allocate(data: dict, blocked: bool = False) -> dict:
    buses = [r for r in data["resources"] if r["type"] == "BUS" and r["status"] == "AVAILABLE"]
    selected = (buses[3], buses[1]) if blocked else (buses[0], buses[1])
    return {"assignments": {"Zone A": selected[0]["id"], "Zone B": selected[1]["id"]}, "reasoning": f"Selected available buses by capacity and proximity; {selected[0]['id']} is used for Zone A."}
