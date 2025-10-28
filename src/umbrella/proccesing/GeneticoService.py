import hashlib
from typing import Dict, Any
import time


def process_data(payload: str) -> Dict[str, Any]:
    """
    Procesa datos genéticos. Es una simulación de CPU-bound REAL,
    dependiente del tamaño del payload.
    """
    print(f"[Worker CPU]... Starting genetic analysis")

    if not payload:
        print(f"[Worker CPU]... ERROR: Payload is empty.")
        return {
            "worker": "CPU-Worker-1",
            "status": "ERROR",
            "details": "Payload cannot be empty."
        }

    iterations = max(1, len(payload) * 5000)

    print(f"[Worker CPU]... Performing {iterations} hash iterations...")

    start_cpu_time = time.monotonic()

    for i in range(iterations):
        _ = hashlib.sha256(f"{payload}{i}".encode()).hexdigest()

    end_cpu_time = time.monotonic()

    sequence_length = len(payload)
    gc_content = (payload.count('G') + payload.count('C')) / sequence_length if sequence_length > 0 else 0

    processing_time = (end_cpu_time - start_cpu_time)
    print(f"[Worker CPU]... Analysis complete in {processing_time:.4f}s.")

    return {
        "worker": "CPU-Worker-1",
        "status": "COMPLETED",
        "details": f"Sequence of {sequence_length} bp (Iter: {iterations}), GC={gc_content:.1%}, Time={processing_time:.2f}s"
    }