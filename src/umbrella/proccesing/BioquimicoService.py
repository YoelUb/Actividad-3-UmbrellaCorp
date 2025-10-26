import asyncio
import json
from typing import Dict, Any



async def process_data(payload: str) -> Dict[str, Any]:
    """
    Procesa datos bioquímicos. Es una simulación de I/O-bound.
    """
    print(f"[Worker I/O]... Querying external composite API (1.5s simulation)")

    try:
        data = json.loads(payload)
        compound = data.get("compound", "unknown")
    except json.JSONDecodeError:
        compound = "payload_invalid"


    await asyncio.sleep(1.5)

    print(f"[Worker I/O]... Querying of {compound} completed.")

    return {
        "worker": "IO-Worker-A",
        "status": "COMPLETED",
        "details": f"Compouse {compound} verificated"
    }