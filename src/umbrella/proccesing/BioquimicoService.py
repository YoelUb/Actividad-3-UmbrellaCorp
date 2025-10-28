import asyncio
import json
from typing import Dict, Any


async def process_data(payload: str) -> Dict[str, Any]:
    """
    Procesa datos bioquímicos. Es una simulación de I/O-bound
    cuyo tiempo de espera depende del tamaño del payload.
    """
    print(f"[Worker I/O]... Querying external composite API")

    if not payload:
        print(f"[Worker I/O]... ERROR: Payload is empty.")
        return {
            "worker": "IO-Worker-A",
            "status": "ERROR",
            "details": "Payload cannot be empty."
        }

    try:
        data = json.loads(payload)
        compound = data.get("compound", "unknown")
    except json.JSONDecodeError:
        compound = "payload_invalid"
        if payload == "{}":
            compound = "empty_payload"


    wait_time = max(0.1, len(payload) / 75.0)

    await asyncio.sleep(wait_time)

    print(f"[Worker I/O]... Querying of {compound} completed in {wait_time:.2f}s.")

    return {
        "worker": "IO-Worker-A",
        "status": "COMPLETED",
        "details": f"Compound {compound} verified (Payload size: {len(payload)} bytes, Wait: {wait_time:.2f}s)"
    }