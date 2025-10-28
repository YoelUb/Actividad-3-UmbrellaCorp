import asyncio
import json
from typing import Dict, Any


async def process_data(payload: str) -> Dict[str, Any]:
    """
    Procesa datos físicos. Es una simulación de I/O-bound
    cuyo tiempo de espera depende del tamaño del payload.
    """
    print(f"[Worker I/O]... Reading sensor data")

    if not payload:
        print(f"[Worker I/O]... ERROR: Payload is empty.")
        return {
            "worker": "IO-Worker-B",
            "status": "ERROR",
            "details": "Payload cannot be empty."
        }

    try:
        data = json.loads(payload)
        sensor_id = data.get("sensor_id", "unknown")
    except json.JSONDecodeError:
        sensor_id = "payload_invalid"
        if payload == "{}":
            sensor_id = "empty_payload"


    wait_time = max(0.1, len(payload) / 200.0)

    await asyncio.sleep(wait_time)

    print(f"[Worker I/O]... Reading of {sensor_id} completed in {wait_time:.2f}s.")

    return {
        "worker": "IO-Worker-B",
        "status": "COMPLETED",
        "details": f"Sensor {sensor_id} OK (Payload size: {len(payload)} bytes, Wait: {wait_time:.2f}s)"
    }