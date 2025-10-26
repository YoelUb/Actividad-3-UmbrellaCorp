import time
import json
from typing import Dict, Any


def process_data(payload: str) -> Dict[str, Any]:
    """
    Procesa datos genéticos. Es una simulación de CPU-bound.
    """
    print(f"[Worker CPU]... Starting genetic analysis (2s simulation)")

    time.sleep(2)

    sequence_length = len(payload)
    gc_content = (payload.count('G') + payload.count('C')) / sequence_length if sequence_length > 0 else 0

    print(f"[Worker CPU]... Analysis complete.")

    return {
        "worker": "CPU-Worker-1",
        "status": "COMPLETED",
        "details": f"Sequence of {sequence_length} base pair, GC={gc_content:.1%}"
    }