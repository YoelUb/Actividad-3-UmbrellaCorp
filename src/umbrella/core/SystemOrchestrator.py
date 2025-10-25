import time
import json
import asyncio
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..proccesing import GeneticoService, BioquimicoService, FisicoService
from ..utils.MetricsMonitor import metrics_monitor
from ..db.models import Evento
from ..model.websockets_manager import ConnectionManager
from ..utils.AlertService import build_and_send_report


class SystemOrchestrator:
    def __init__(self, session: AsyncSession, ws_manager: ConnectionManager):
        self.session = session
        self.ws_manager = ws_manager
        self.loop = asyncio.get_running_loop()

    async def handle_ingestion(self, ingest_data: Dict[str, Any]):

        event_id = ingest_data.get("id", "UNKNOWN_ID")
        tipo_dato = ingest_data.get("tipo", "UNKNOWN_TYPE")
        payload = ingest_data.get("payload", "{}")
        recipient_email = ingest_data.get("recipient_email")  # <-- ¡NUEVO!

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
        metrics_monitor.record_latency(tipo_dato, start_time, end_time)

        await self.save_event_to_db(event_id, tipo_dato, result)

        await self.broadcast_alert_and_email(event_id, tipo_dato, result, recipient_email)

        print(f"[Orchestrator] Processing completed for {event_id}")

    async def save_event_to_db(self, event_id: str, tipo_dato: str, result: Dict[str, Any]):
        nuevo_evento = Evento(
            event_id=event_id,
            tipo_dato=tipo_dato,
            worker=result.get("worker", "N/A"),
            status=result.get("status", "UNKNOWN")
        )
        self.session.add(nuevo_evento)
        await self.session.commit()


    async def broadcast_alert_and_email(
            self, event_id: str, tipo_dato: str, result: Dict[str, Any], recipient_email: str
    ):
        """
        Envía el resultado a los clientes web Y delega el informe por email
        si es crítico.
        """
        level = "error" if result.get(
            'status') == "ERROR" else "critical" if tipo_dato == "genetico" else "warning"

        alert_data = {
            "title": f"EVENT: {tipo_dato.upper()} ({result.get('status')})",
            "message": f"ID {event_id} processed by {result.get('worker')}. Details: {result.get('details', '')}",
            "level": level
        }

        await self.ws_manager.broadcast(json.dumps(alert_data))


        if (level == "critical" or level == "error") and recipient_email:
            print(f"[Orchestrator] Alerta {level} detectada. Delegando a AlertService para {recipient_email}...")
            subject = f"Alerta de Umbrella Corp: {alert_data['title']}"

            await build_and_send_report(
                session=self.session,
                metrics_monitor=metrics_monitor,
                subject=subject,
                alert_message=alert_data['message'],
                event_id=event_id,
                tipo_dato=tipo_dato,
                recipient_email=recipient_email
            )
        elif level == "critical" or level == "error":
            print(f"[Orsechtrator] Alerta {level} detectada, pero no se proporcionó email.")