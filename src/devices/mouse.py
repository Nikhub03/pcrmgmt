import sys
import time
from .base import Device
from ..core.logger import log_info


class Mouse(Device):
    def get_metrics(self): return {}
    def get_status(self): return {"mouse": "ok"}

    def monitor(self, interval: float = 0.1, duration: float = 5.0):
        log_info("MOUSE", "mouse monitor started")
        if sys.platform == "win32":
            import ctypes
            user32 = ctypes.windll.user32
            screen_w = user32.GetSystemMetrics(0)
            screen_h = user32.GetSystemMetrics(1)
            end = time.time() + duration
            while time.time() < end:
                pt = ctypes.wintypes.POINT() if False else None
                # ctypes.wintypes требует import
                import ctypes.wintypes as wt
                p = wt.POINT()
                user32.GetCursorPos(ctypes.byref(p))
                if not (0 <= p.x <= screen_w and 0 <= p.y <= screen_h):
                    print(f"Cursor out of bounds: X={p.x}, Y={p.y}")
                else:
                    print(f"X={p.x}, Y={p.y}")
                time.sleep(interval)
        else:
            print("(mouse monitor: только Windows в данной сборке)")
        log_info("MOUSE", "mouse monitor stopped")