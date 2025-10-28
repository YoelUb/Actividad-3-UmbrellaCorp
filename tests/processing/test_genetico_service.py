from src.umbrella.proccesing.GeneticoService import process_data


def test_process_genetico_data():
    """
    Prueba que el servicio genético procese correctamente
    un payload simple.
    """
    payload = "AGGC"

    result = process_data(payload)

    assert result["status"] == "COMPLETED"
    assert result["worker"] == "CPU-Worker-1"
    assert "Sequence of 4" in result["details"]
    assert "GC=75.0%" in result["details"]
    assert "Time=" in result["details"]


def test_process_genetico_data_empty():
    """Prueba el caso de un payload vacío."""
    payload = ""
    result = process_data(payload)

    # Ahora esperamos un ERROR
    assert result["status"] == "ERROR"
    assert result["worker"] == "CPU-Worker-1"
    assert "Payload cannot be empty" in result["details"]

