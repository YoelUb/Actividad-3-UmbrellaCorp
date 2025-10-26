import time
import datetime
from collections import deque
from typing import Deque, List, Dict, Any, Tuple

MAX_METRICS = 50


class MetricsMonitor:
    def __init__(self):
        self.latency_data: Dict[str, Deque[Tuple[datetime.datetime, float]]] = {
            "genetico": deque(maxlen=MAX_METRICS),
            "bioquimico": deque(maxlen=MAX_METRICS),
            "fisico": deque(maxlen=MAX_METRICS),
            "unknown": deque(maxlen=MAX_METRICS),
        }

        self.last_reported_time: Dict[str, datetime.datetime] = {}

    def record_latency(self, tipo_dato: str, start_time: float, end_time: float):
        """Registra una nueva medición de latencia para un tipo específico."""
        latencia_ms = (end_time - start_time) * 1000
        timestamp = datetime.datetime.now()

        deque_key = tipo_dato if tipo_dato in self.latency_data else "unknown"
        self.latency_data[deque_key].append((timestamp, latencia_ms))

        print(f"Registry latency for {tipo_dato}: {latencia_ms:.2f} ms")

    def get_all_last_latencies(self) -> Dict[str, Any]:
        """
        Obtiene la última latencia registrada de CADA tipo
        solo si no ha sido reportada antes.
        """
        now_str = datetime.datetime.now().strftime("%H:%M:%S")

        def get_latest_or_default(tipo):
            if not self.latency_data[tipo]:
                return {"time": now_str, "latency": 0}

            last_timestamp, last_latency = self.latency_data[tipo][-1]

            if self.last_reported_time.get(tipo) == last_timestamp:
                return {"time": now_str, "latency": 0}
            else:

                self.last_reported_time[tipo] = last_timestamp
                return {
                    "time": last_timestamp.strftime("%H:%M:%S"),
                    "latency": last_latency
                }

        return {
            "genetico": get_latest_or_default("genetico"),
            "bioquimico": get_latest_or_default("bioquimico"),
            "fisico": get_latest_or_default("fisico")
        }


metrics_monitor = MetricsMonitor()
