import smtplib
import os
import asyncio
import datetime
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..db.models import Evento
from ..utils.MetricsMonitor import MetricsMonitor

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")



async def build_and_send_report(
        session: AsyncSession,
        metrics_monitor: MetricsMonitor,
        subject: str,
        alert_message: str,
        event_id: str,
        tipo_dato: str,
        recipient_email: str  # <-- El email del usuario
):
    """
    Construye un informe completo y luego llama a la función síncrona
    de envío de email en un executor.
    """
    print(f"[AlertService] Construyendo informe completo para {event_id}...")

    reporte_completo = f"""
==================================================
INFORME DE ALERTA CRÍTICA - UMBRELLA CORPORATION
==================================================
Fecha: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Evento ID: {event_id}
Tipo: {tipo_dato}

--------------------------------------------------
DETALLES DE LA ALERTA:
--------------------------------------------------
{alert_message}

"""

    reporte_completo += """
--------------------------------------------------
DATOS DE LATENCIA RECIENTE (ms):
--------------------------------------------------
"""
    try:
        for tipo, data_deque in metrics_monitor.latency_data.items():
            if not data_deque:
                reporte_completo += f"- {tipo.upper()}: N/A\n"
            else:
                ultimas_5 = list(data_deque)[-5:]
                reporte_completo += f"- {tipo.upper()}:\n"
                for timestamp, lat in ultimas_5:
                    reporte_completo += f"    {timestamp.strftime('%H:%M:%S')} -> {lat:.2f} ms\n"
    except Exception as e:
        reporte_completo += f"Error al obtener métricas: {e}\n"

    reporte_completo += """
--------------------------------------------------
ÚLTIMOS 5 EVENTOS DEL SISTEMA:
--------------------------------------------------
"""
    try:
        statement = select(Evento).order_by(Evento.created_at.desc()).limit(5)
        db_result = await session.execute(statement)
        events = db_result.scalars().all()
        if not events:
            reporte_completo += "No hay eventos en la base de datos.\n"
        for ev in events:
            reporte_completo += (
                f"[{ev.created_at.strftime('%H:%M:%S')}] "
                f"ID: {ev.event_id} | "
                f"Tipo: {ev.tipo_dato} | "
                f"Status: {ev.status}\n"
            )
    except Exception as e:
        reporte_completo += f"Error al consultar la base de datos: {e}\n"
    reporte_completo += "\n==================================================\nFin del Informe.\n"

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        _send_email_sync,
        subject,
        reporte_completo,
        event_id,
        recipient_email
    )


def _send_email_sync(
        subject: str, body_content: str, event_id: str, recipient_email: str  # <-- Acepta el email del usuario
):
    """
    Envía el email (función síncrona y bloqueante).
    """

    if not all([EMAIL_SENDER, EMAIL_APP_PASSWORD]):
        print("[EmailService] Error: Faltan variables SENDER o APP_PASSWORD en .env.")
        return

    if not recipient_email:
        print("[EmailService] Error: No se ha proporcionado un email de destinatario.")
        return

    print(f"[EmailService] Preparando email (con adjunto) para {recipient_email}...")

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    # --- CAMBIO 3: 'To' corregido ---
    msg['To'] = recipient_email

    email_body_text = "Se ha detectado una alerta crítica. Se adjunta el informe .txt con los detalles."
    msg.attach(MIMEText(email_body_text, 'plain'))

    filename = f"informe_alerta_{event_id}.txt"
    part = MIMEBase('application', "octet-stream")
    part.set_payload(body_content.encode('utf-8'))
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={filename}')
    msg.attach(part)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
            smtp_server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())
        print(f"[EmailService] ¡Mensaje con adjunto enviado con éxito!")
    except Exception as e:
        print(f"[EmailService] Error al enviar email: {e}")