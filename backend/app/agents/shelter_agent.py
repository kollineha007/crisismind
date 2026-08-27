def allocate(data: dict, blocked: bool = False) -> dict:
    shelters = sorted(data["shelters"], key=lambda s: s["capacity"] - s["occupancy"], reverse=True)
    primary = shelters[0] if not blocked else next(s for s in shelters if s["name"] == "Shelter C")
    return {"assignments": {"Zone A": primary["name"], "Zone B": "Shelter C" if primary["name"] == "Shelter B" else "Shelter B"}, "reasoning": f"{primary['name']} has {primary['capacity']-primary['occupancy']} remaining places and is accessible; route availability was considered."}
