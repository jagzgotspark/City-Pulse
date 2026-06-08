from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from src.api.routes import router
from src.utils.database import init_db
import threading
from src.scheduler import run_scheduler

app = FastAPI(
    title="City Pulse API",
    description="Real-time city pulse scores",
    version="1.0.0"
)

async def broadcast(data: dict):
    dead = []
    for ws in connected_clients:
        try:
            await ws.send_json(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        connected_clients.remove(ws)

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def startup():
    init_db()
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"status": "City Pulse API is running"}