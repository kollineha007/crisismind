from datetime import datetime, timezone
from uuid import uuid4
from .websocket_manager import manager

class EventManager:
    def __init__(self):
        self.events: list[dict] = []

    async def publish(self, event_type: str, source: str, message: str, location: str, agent_id: str | None = None, severity: str = "INFO", data: dict | None = None, status: str = "COMPLETED") -> dict:
        event = {
            "id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "severity": severity,
            "source": source,
            "agent_id": agent_id,
            "agent": agent_id,
            "message": message,
            "location": location,
            "data": data or {},
            "status": status,
        }
        self.events.append(event)
        await manager.broadcast(event)
        return event
