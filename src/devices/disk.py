import random
import psutil
from .base import Device
from ..core.cache import CACHE
from ..core.logger import log_warning

_rng = random.Random(7)


class Disk(Device):
    def get_metrics(self) -> dict:
        cached = CACHE.get("disk.metrics")
        if cached:
            return cached
        disks = []
        try:
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                except (PermissionError, OSError):
                    continue
                disks.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fs": part.fstype,
                    "total_gb": round(usage.total / (1024 ** 3), 1),
                    "used_gb": round(usage.used / (1024 ** 3), 1),
                    "free_gb": round(usage.free / (1024 ** 3), 1),
                    "percent": round(usage.percent, 1),
                    "temperature_c": _rng.randint(28, 50),
                    "temperature_simulated": True,
                    "smart": "OK",
                })
        except Exception as e:
            log_warning("DISK", f"psutil error: {e}")
        data = {"disks": disks}
        CACHE.set("disk.metrics", data, ttl=5.0)
        return data

    def get_status(self) -> dict:
        m = self.get_metrics()
        max_used = max((d["percent"] for d in m["disks"]), default=0.0)
        return {"disk_max_percent": max_used}
