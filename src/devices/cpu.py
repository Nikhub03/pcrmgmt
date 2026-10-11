import platform
import random
import psutil
from .base import Device
from ..core.cache import CACHE
from ..core.logger import log_warning, log_info

_rng = random.Random(42)


class CPU(Device):
    def __init__(self):
        self._model = self._detect_model()
        log_info("CPU", f"detected model: {self._model}")

    @staticmethod
    def _detect_model() -> str:
        try:
            return platform.processor() or "Unknown CPU"
        except Exception:
            return "Unknown CPU"

    def get_metrics(self) -> dict:
        cached = CACHE.get("cpu.metrics")
        if cached:
            return cached

        try:
            per_core = psutil.cpu_percent(interval=None, percpu=True)
            overall = sum(per_core) / len(per_core) if per_core else 0.0
            freq = psutil.cpu_freq()
            freq_ghz = round(freq.current / 1000, 1) if freq else 0.0
            temp = self._read_temperature()
        except Exception as e:
            log_warning("CPU", f"psutil failed: {e}")
            per_core, overall, freq_ghz, temp = [0.0], 0.0, 0.0, 0.0

        data = {
            "model": self._model,
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "load_percent": round(overall, 1),
            "load_per_core": [round(v, 1) for v in per_core],
            "frequency_ghz": freq_ghz,
            "temperature_c": temp,
            "temperature_simulated": True,
        }
        CACHE.set("cpu.metrics", data, ttl=1.0)
        return data

    def _read_temperature(self) -> int:
        # Windows без сторонних драйверов не даёт доступа → симуляция
        try:
            sensors = psutil.sensors_temperatures()
            if sensors:
                for name, entries in sensors.items():
                    if entries:
                        return int(entries[0].current)
        except Exception:
            pass
        return _rng.randint(35, 70)

    def get_status(self) -> dict:
        m = self.get_metrics()
        return {"cpu_load": m["load_percent"], "cpu_temp": m["temperature_c"]}