import json
import asyncio
import os
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from ..orchestrator import MythosOrchestrator

app = FastAPI(title="Mythos Latent API")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    task: str
    dry_run: bool = False
    verbose: bool = True

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()
# Lazy load orchestrator to avoid loading model on import
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MythosOrchestrator(web_mode=True)
    return _orchestrator

@app.get("/api/health")
async def health_check():
    return {"status": "alive", "engine": "OpenMythos"}

@app.websocket("/ws/state")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({"type": "INIT", "data": {"status": "connected"}})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/stream/update")
async def receive_update(update: dict):
    await manager.broadcast(update)
    return {"status": "broadcasted"}

@app.post("/api/task/run")
async def run_task(request: TaskRequest, background_tasks: BackgroundTasks):
    orch = get_orchestrator()
    orch.dry_run = request.dry_run
    orch.verbose = request.verbose
    background_tasks.add_task(execute_orchestrator, request.task)
    return {"status": "started", "task": request.task}

async def execute_orchestrator(task: str):
    orch = get_orchestrator()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, orch.execute_task, task)

@app.get("/api/memory")
async def get_memory():
    orch = get_orchestrator()
    entries = orch.memory.search("%")
    return {"entries": entries}

@app.get("/api/stats")
async def get_stats():
    orch = get_orchestrator()
    return orch.metrics.get_stats()

# Serve static files from the React build
static_dir = os.path.join(os.path.dirname(__file__), "ui/dist")
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("ws/"):
            return None # Should be handled by other routes
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    @app.get("/")
    async def root_fallback():
        return {"message": "WebUI source not found. Please run 'npm run build' in the ui directory."}

def start_server(host="0.0.0.0", port=8000):
    print(f"Starting Mythos Latent API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
