import random
from .base import Device
from ..core.cache import CACHE

_rng = random.Random(13)


class GPU(Device):
    """Симулированный GPU (реальный доступ требует nvidia-ml-py)."""
    def get_metrics(self) -> dict:
        cached = CACHE.get("gpu.metrics")
        if cached:
            return cached
        data = {
            "model": "Simulated GPU",
            "memory_total_gb": 6,
            "load_percent": _rng.randint(0, 100),
            "temperature_c": _rng.randint(35, 75),
            "simulated": True,
        }
        CACHE.set("gpu.metrics", data, ttl=5.0)
        return data

    def get_status(self) -> dict:
        m = self.get_metrics()
        return {"gpu_load": m["load_percent"], "gpu_temp": m["temperature_c"]}