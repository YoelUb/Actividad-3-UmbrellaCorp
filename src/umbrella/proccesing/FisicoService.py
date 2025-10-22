import asyncio
import json
from typing import Dict, Any



async def process_data(payload: str) -> Dict[str, Any]:
    """
    Procesa datos físicos. Es una simulación de I/O-bound.
    """
    print(f"[Worker I/O]... Reading sensor data (0.5s simulation)")

    try:
        data = json.loads(payload)
        sensor_id = data.get("sensor_id", "unknown")
    except json.JSONDecodeError:
        sensor_id = "payload_invalid"

    await asyncio.sleep(0.5)

    print(f"[Worker I/O]... Reading of {sensor_id} completed.")

    return {
        "worker": "IO-Worker-B",
        "status": "COMPLETED",
        "details": f"Sensor {sensor_id} OK"
    }