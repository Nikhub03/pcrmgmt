import hashlib
import os
import sys
import time
from datetime import datetime
from .base import Device
from ..core.logger import log_info, log_error, log_warning
from ..core.errors import DeviceNotFound, InvalidArgument


PRINT_LOG = "print_output.txt"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ


class Printer(Device):
    def list_printers(self) -> list[str]:
        if sys.platform == "win32":
            try:
                import win32print
                return [p[2] for p in win32print.EnumPrinters(
                    win32print.PRINTER_ENUM_LOCAL)]
            except Exception as e:
                log_warning("PRINTER", f"EnumPrinters failed: {e}")
        return ["Simulated_Printer"]

    def get_metrics(self) -> dict:
        return {"printers": self.list_printers()}

    def get_status(self) -> dict:
        return {"printers": self.list_printers()}

    def print_text(self, text: str):
        printers = self.list_printers()
        if not printers:
            raise DeviceNotFound("No printers detected (simulation)")
        name = printers[0]
        ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        pid = os.getpid()
        line = (f"[{ts}] PID={pid} Printer={name} STATUS=PRINTED "
                f"TEXT={text[:50]}")
        with open(PRINT_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        log_info("PRINTER", f"printed text to {name}: {text[:30]}")
        return {"printer": name, "status": "PRINTED", "text": text}

    def print_file(self, path: str):
        if not os.path.exists(path):
            raise DeviceNotFound(f"Cannot read file <{path}>: not found")
        size = os.path.getsize(path)
        if size > MAX_FILE_SIZE:
            raise InvalidArgument("File too large (max 10 MB)")
        try:
            with open(path, "rb") as f:
                raw = f.read()
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise InvalidArgument("Invalid encoding: use UTF-8")

        printers = self.list_printers()
        name = printers[0] if printers else "Simulated_Printer"
        ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        pid = os.getpid()
        md5 = hashlib.md5(raw).hexdigest() if size > 1024 else "-"
        mb = size / (1024 * 1024)
        line = (f"[{ts}] PID={pid} Printer={name} STATUS=PRINTED "
                f"FILE={path} ({mb:.2f} MB, MD5={md5})")
        with open(PRINT_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        log_info("PRINTER", f"printed file {path} to {name}")
        return {"printer": name, "file": path, "md5": md5, "size": size}