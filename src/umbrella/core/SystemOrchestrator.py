import time
import json
import asyncio
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..proccesing import GeneticoService, BioquimicoService, FisicoService
from ..utils.MetricsMonitor import metrics_monitor
from ..db.models import Evento
from ..model.websockets_manager import ConnectionManager


class SystemOrchestrator:
    def __init__(self, session: AsyncSession, ws_manager: ConnectionManager):
        self.session = session
        self.ws_manager = ws_manager
        self.loop = asyncio.get_running_loop()

    async def handle_ingestion(self, ingest_data: Dict[str, Any]):
        """
        Punto de entrada para procesar un solo dato.
        Sigue el flujo: Ingesta -> Procesamiento (Worker) -> Almacenamiento -> Alerta
        """

        event_id = ingest_data.get("id", "UNKNOWN_ID")
        tipo_dato = ingest_data.get("tipo", "UNKNOWN_TYPE")
        payload = ingest_data.get("payload", "{}")

        print(f"[Orchestrator] Starting processing for {event_id} (Type: {tipo_dato})")

        start_time = time.monotonic()

        try:
            if tipo_dato == "genetico":

                print(f"[Orchestrator] Delegating {event_id} to a ThreadPool (CPU-bound)")
                result = await self.loop.run_in_executor(
                    None,
                    GeneticoService.process_data,
                    payload
                )

            elif tipo_dato == "bioquimico":

                result = await BioquimicoService.process_data(payload)

            elif tipo_dato == "fisico":

                result = await FisicoService.process_data(payload)

            else:
                result = {"worker": "N/A", "status": "REJECTED", "details": "Data type not supported"}

        except Exception as e:
            print(f"[Orchestrator] ERROR processing {event_id}: {e}")
            result = {"worker": "Error", "status": "ERROR", "details": str(e)}


        end_time = time.monotonic()
        metrics_monitor.record_latency(start_time, end_time)


        await self.save_event_to_db(event_id, tipo_dato, result)


        await self.broadcast_alert(event_id, tipo_dato, result)

        print(f"[Orchestrator] Processing completed for {event_id}")

    async def save_event_to_db(self, event_id: str, tipo_dato: str, result: Dict[str, Any]):
        """Guarda el resultado en la base de datos."""
        nuevo_evento = Evento(
            event_id=event_id,
            tipo_dato=tipo_dato,
            worker=result.get("worker", "N/A"),
            status=result.get("status", "UNKNOWN")
        )
        self.session.add(nuevo_evento)
        await self.session.commit()

    async def broadcast_alert(self, event_id: str, tipo_dato: str, result: Dict[str, Any]):
        """Envía el resultado a todos los clientes web conectados."""
        alert_data = {
            "title": f"EVENT: {tipo_dato.upper()} ({result.get('status')})",
            "message": f"ID {event_id} processed by {result.get('worker')}. Details: {result.get('details', '')}",
            "level": "error" if result.get(
                'status') == "ERROR" else "critical" if tipo_dato == "genetico" else "warning"
        }
        await self.ws_manager.broadcast(json.dumps(alert_data))