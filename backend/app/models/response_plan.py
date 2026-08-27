from datetime import datetime
from typing import Any
from pydantic import BaseModel

class Recommendation(BaseModel):
    priority: str
    action: str
    reason: str
    affected_area: str
    assigned_resource: str | None = None
    approval_status: str = "PENDING"
    what: str
    data_used: list[str]
    confidence: int
    alternatives: list[str]

class ResponsePlan(BaseModel):
    version: int
    status: str = "PENDING APPROVAL"
    created_at: datetime
    recommendations: list[Recommendation]
    explanation: list[str]
    changes: list[str] = []

class AuditEntry(BaseModel):
    timestamp: datetime
    agent: str
    action: str
    reason: str
    data_used: list[str]
    plan_version: int
    human_approval: str
    event_type: str

class AgentEvent(BaseModel):
    timestamp: datetime
    agent: str
    status: str
    message: str
    event_type: str
