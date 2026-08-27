from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

class CrisisInput(BaseModel):
    disaster_type: str = "FLOOD"
    location: str = "Vijayawada"
    water_level: float = Field(2.4, ge=0)
    affected_population: int = Field(8500, ge=0)
    blocked_roads: int = Field(2, ge=0)
    reports: list[str] = []
    timestamp: datetime | None = None

class Assessment(BaseModel):
    disaster_type: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    affected_population: int
    priority_zones: list[str]
    urgency: str
    medical_risk: str
    evacuation_required: bool
    reasoning: str

class SituationChange(BaseModel):
    event_type: str
    description: str
    timestamp: datetime
