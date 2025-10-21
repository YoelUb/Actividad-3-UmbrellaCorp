from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.responses import HTMLResponse
from starlette.requests import Request

from src.umbrella import data

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


#Clase de los datos que obtenemos del formulario
class ManualIngestData(BaseModel):
    id: str
    tipo: str
    payload: str | None = None

@app.post("/api/ingest/manual")
async def ingest_manual_data(data: ManualIngestData):
    """
    Endpoint para recibir datos manualmente desde el front-end.
    """
    #Se devuelve un json
    return {"status": "ok", "task_id": data.id, "message": "Tarea encolada para procesamiento"}


