import random
from .base import Device
from ..core.cache import CACHE
from ..core.logger import log_info

_rng = random.Random(21)
_fan_speed = {0: 1200, 1: 1500, 2: 1800}


class Fan(Device):
    def get_metrics(self) -> dict:
        cached = CACHE.get("fan.metrics")
        if cached:
            return cached
        fans = [{"id": i, "rpm": _fan_speed[i], "simulated": True}
                for i in sorted(_fan_speed)]
        data = {"fans": fans}
        CACHE.set("fan.metrics", data, ttl=5.0)
        return data

    def set_speed(self, device_id: int, speed_percent: int):
        if not 0 <= speed_percent <= 100:
            from ..core.errors import InvalidArgument
            raise InvalidArgument("speed must be in 0..100")
        rpm = int(500 + (speed_percent / 100) * 2500)
        _fan_speed[device_id] = rpm
        CACHE.clear()
        log_info("FAN", f"fan {device_id} set to {speed_percent}% ({rpm} RPM, simulated)")
        return {"device": device_id, "speed_percent": speed_percent, "rpm": rpm}

    def get_status(self) -> dict:
        return {"fans": self.get_metrics()["fans"]}