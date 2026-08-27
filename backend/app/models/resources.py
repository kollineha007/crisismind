from typing import Literal
from pydantic import BaseModel

class Resource(BaseModel):
    id: str
    type: str
    location: str
    capacity: int
    status: Literal["AVAILABLE", "ASSIGNED", "UNAVAILABLE"]
    assigned_zone: str | None = None
    availability: bool = True

class Shelter(BaseModel):
    name: str
    zone: str
    latitude: float
    longitude: float
    capacity: int
    occupancy: int
    accessibility: str
    status: str

    @property
    def remaining(self) -> int:
        return self.capacity - self.occupancy

class Hospital(BaseModel):
    name: str
    latitude: float
    longitude: float
    total_beds: int
    available_beds: int
    icu_beds: int
    ambulances: int
    status: str
