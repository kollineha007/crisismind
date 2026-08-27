from fastapi import WebSocket
class ConnectionManager:
    def __init__(self): self.connections: list[WebSocket] = []
    async def connect(self, ws): await ws.accept(); self.connections.append(ws)
    def disconnect(self, ws):
        if ws in self.connections: self.connections.remove(ws)
    async def broadcast(self, event):
        for ws in self.connections[:]:
            try: await ws.send_json(event)
            except Exception: self.disconnect(ws)
manager = ConnectionManager()
