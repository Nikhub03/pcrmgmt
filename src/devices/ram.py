import psutil
from .base import Device
from ..core.cache import CACHE


class RAM(Device):
    def get_metrics(self) -> dict:
        cached = CACHE.get("ram.metrics")
        if cached:
            return cached
        vm = psutil.virtual_memory()
        data = {
            "total_gb": round(vm.total / (1024 ** 3), 1),
            "used_gb": round(vm.used / (1024 ** 3), 1),
            "free_gb": round(vm.available / (1024 ** 3), 1),
            "percent": round(vm.percent, 1),
        }
        CACHE.set("ram.metrics", data, ttl=1.0)
        return data

    def get_status(self) -> dict:
        m = self.get_metrics()
        return {"ram_percent": m["percent"], "ram_used_gb": m["used_gb"]}