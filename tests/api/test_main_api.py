import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.umbrella.db.models import Evento


@pytest.mark.asyncio
async def test_ingest_manual_api(client: AsyncClient, session: AsyncSession):
    """
    Prueba el endpoint de ingesta /api/ingest/manual
    """
    test_data = {
        "id": "API-TEST-001",
        "tipo": "fisico",
        "payload": '{"sensor_id": "T-API"}',
        "recipient_email": "tests@dominio.com"
    }

    response = await client.post("/api/ingest/manual", json=test_data)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "ok"
    assert "Data for API-TEST-001 received" in json_response["message"]

    statement = select(Evento).where(Evento.event_id == "API-TEST-001")
    db_result = await session.execute(statement)
    evento_guardado = db_result.scalar_one_or_none()

    assert evento_guardado is not None
    assert evento_guardado.tipo_dato == "fisico"
    assert evento_guardado.status == "COMPLETED"
    assert evento_guardado.worker == "IO-Worker-B"