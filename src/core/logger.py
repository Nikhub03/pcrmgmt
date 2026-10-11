"""Централизованное структурированное логирование."""
import logging
import os
from datetime import datetime

LOG_FILE = "app.log"


class _Formatter(logging.Formatter):
    def format(self, record):
        ts = datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%dT%H:%M:%S"
        ) + f",{int(record.msecs):03d}"
        level = record.levelname[:5].ljust(5)
        component = getattr(record, "component", "APP")
        return f"{ts} {level} {component} {record.getMessage()}"


def _build_logger():
    logger = logging.getLogger("pcrmgmt")
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        return logger

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_Formatter())
    logger.addHandler(fh)

    # Права 600 на лог-файл (в Linux; в Windows игнорируем)
    try:
        os.chmod(LOG_FILE, 0o600)
    except OSError:
        pass

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(_Formatter())
    logger.addHandler(ch)
    return logger


LOG = _build_logger()


def log(level: str, component: str, message: str):
    LOG.log(getattr(logging, level.upper()), message, extra={"component": component})


def log_debug(component, msg):   log("DEBUG",   component, msg)
def log_info(component, msg):    log("INFO",    component, msg)
def log_warning(component, msg): log("WARNING", component, msg)
def log_error(component, msg):   log("ERROR",   component, msg)