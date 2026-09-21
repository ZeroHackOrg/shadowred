# src/shadowred/metrics.py
import threading
from typing import Dict, List


class ShadowRedMetricsRegistry:
    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._lock = threading.Lock()

    def counter(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

    def gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = float(value)

    def snapshot(self) -> dict:
        with self._lock:
            return {"counters": dict(self._counters), "gauges": dict(self._gauges)}

    def prometheus_text(self) -> str:
        snap = self.snapshot()
        lines = []
        for name, value in snap["counters"].items():
            metric = f"sred_{name}"
            lines.append(f"# TYPE {metric} counter")
            lines.append(f"{metric} {value}")
        for name, value in snap["gauges"].items():
            metric = f"sred_{name}"
            lines.append(f"# TYPE {metric} gauge")
            lines.append(f"{metric} {value}")
        return "\n".join(lines)


DEFAULT_METRICS = ShadowRedMetricsRegistry()