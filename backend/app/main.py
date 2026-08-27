from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .api.crisis_routes import router as crisis_router
from .api.agent_routes import router as agent_router
from .api.simulation_routes import router as simulation_router
from .services.websocket_manager import manager
app=FastAPI(title="CrisisMind AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(crisis_router); app.include_router(agent_router); app.include_router(simulation_router)
@app.get("/api/health")
def health():
    from .services.llm_service import llm_service
    return {"status":"online","mode":"REAL AI - GEMINI" if llm_service.active else "DEMO MODE - FALLBACK AI","database":"local JSON/in-memory"}
@app.websocket("/ws/crisis")
async def websocket(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: manager.disconnect(ws)

@app.websocket("/ws/events")
async def events_websocket(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: manager.disconnect(ws)
