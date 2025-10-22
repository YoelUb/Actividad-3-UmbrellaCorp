from typing import List

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.future import select
from starlette.responses import HTMLResponse
from starlette.requests import Request
from starlette.websockets import WebSocket, WebSocketDisconnect

from .umbrella.core.SystemOrchestrator import SystemOrchestrator
from .umbrella.db.database import lifespan, session_dep
from .umbrella.db.models import Evento
from .umbrella.model.websockets_manager import manager
from .umbrella.utils.MetricsMonitor import metrics_monitor

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

#Landing page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

#Websockets endpoint
@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("Cliente WebSocket connected")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Cliente WebSocket disconnected")


# Latency
@app.get("/api/metrics/latency")
async def get_latency():
    return metrics_monitor.get_last_latency()

# DB
@app.get("/api/events/recent", response_model=List[Evento])
async def get_recent_events(session: session_dep):
    statement = select(Evento).order_by(Evento.created_at.desc()).limit(10)
    result = await session.execute(statement)
    events = result.scalars().all()
    return events


class IngestData(BaseModel):
    id: str
    tipo: str
    payload: str


@app.post("/api/ingest/manual")
async def ingest_manual(data: IngestData, session: session_dep):

    orchestrator = SystemOrchestrator(session, manager)


    await orchestrator.handle_ingestion(data.dict())

    return {"status": "ok", "message": f"Data for {data.id} received and being processed."}
