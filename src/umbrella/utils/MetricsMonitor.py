import time
import datetime
from collections import deque
from typing import Deque, List, Dict, Any, Tuple

MAX_METRICS = 50


class MetricsMonitor:
    def __init__(self):
        self.latency_data: Deque[Tuple[datetime.datetime, float]] = deque(maxlen=MAX_METRICS)

    def record_latency(self, start_time: float, end_time: float):
        """Registra una nueva medición de latencia."""
        latencia_ms = (end_time - start_time) * 1000
        timestamp = datetime.datetime.now()
        self.latency_data.append((timestamp, latencia_ms))
        print(f"Latencia registrada: {latencia_ms:.2f} ms")

    def get_last_latency(self) -> Dict[str, Any]:
        """Obtiene la última latencia registrada para el gráfico."""
        if not self.latency_data:
            return {
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "latency": 0
            }

        last_timestamp, last_latency = self.latency_data[-1]
        return {
            "time": last_timestamp.strftime("%H:%M:%S"),
            "latency": last_latency
        }



metrics_monitor = MetricsMonitor()