import pytest
from src.umbrella.proccesing.FisicoService import process_data


@pytest.mark.asyncio
async def test_process_fisico_data():
    """
    Prueba que el servicio físico procese correctamente
    un payload JSON.
    """
    payload = '{"sensor_id": "T-1000", "temp_celsius": 37.5}'


    result = await process_data(payload)

    assert result["status"] == "COMPLETED"
    assert result["worker"] == "IO-Worker-B"
    assert result["details"] == "Sensor T-1000 OK"


@pytest.mark.asyncio
async def test_process_fisico_data_invalid_json():
    """Prueba qué pasa si el payload no es un JSON válido."""
    payload = "esto no es un json"
    result = await process_data(payload)

    assert result["status"] == "COMPLETED"
    assert result["details"] == "Sensor payload_invalid OK"