from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

class Recommendation(BaseModel):
    id: str = Field(default_factory=lambda: "REC-001")
    priority: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    action: str
    reason: str
    agent: str = "Commander Agent"
    affected_area: str
    affected_count: Optional[int] = None
    assigned_resource: Optional[str] = None
    approval_status: str = "PENDING"  # PENDING, APPROVED, REJECTED, EXECUTED
    execution_status: str = "NOT_EXECUTED"  # NOT_EXECUTED, SIMULATED, COMPLETED
    what: str = ""
    data_used: list[str] = []
    confidence: int = 90
    alternatives: list[str] = []
    action_type: str = "GENERIC"  # BLOCK_ROAD, EVACUATE_ZONE, ALLOCATE_RESOURCE, RESERVE_BEDS, OPEN_SHELTER, BROADCAST_ALERT

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

