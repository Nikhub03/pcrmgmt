import sys
import time
from .base import Device
from ..core.logger import log_info


class Keyboard(Device):
    """Неблокирующее чтение клавиш (Windows: msvcrt, Linux: termios)."""

    def get_metrics(self): return {}
    def get_status(self): return {"keyboard": "ok"}

    def monitor(self, timeout: float = 30.0):
        log_info("KEYBOARD", "keyboard monitor started")
        print("Нажмите Esc для выхода. Тайм-аут: 30 с.")
        if sys.platform == "win32":
            import msvcrt
            start = time.time()
            last = start
            while True:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    last = time.time()
                    if ch == "\x1b":
                        break
                    print(f"Pressed: {repr(ch)}")
                if time.time() - last > timeout:
                    print("No input detected, exiting keyboard mode")
                    break
                time.sleep(0.01)
        else:
            print("(keyboard monitor: только Windows в данной сборке)")
        log_info("KEYBOARD", "keyboard monitor stopped")