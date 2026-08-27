def allocate(data: dict) -> dict:
    hospitals = sorted(data["hospitals"], key=lambda h: (h["icu_beds"], h["available_beds"]), reverse=True)
    chosen = hospitals[0]
    return {"hospital": chosen["name"], "available_beds": chosen["available_beds"], "icu_beds": chosen["icu_beds"], "reasoning": f"{chosen['name']} leads with {chosen['available_beds']} available beds and {chosen['icu_beds']} ICU beds."}
