"""Конфигурация приложения (YAML/JSON) с валидацией."""
import json
import os
import yaml
from .logger import log_warning, log_info


DEFAULT = {
    "thresholds": {"cpu_temp": 80, "ram_usage": 90, "disk_usage": 95},
    "printer": {"name": "HP_LaserJet_1020", "timeout": 30},
    "monitor": {"default_interval": 2.0, "min_interval": 0.5},
}


def load_config(path: str | None = None) -> dict:
    data = dict(DEFAULT)
    if not path:
        for candidate in ("config.yaml", "config.json"):
            if os.path.exists(candidate):
                path = candidate
                break
    if not path or not os.path.exists(path):
        log_warning("CONFIG", "config not found, using defaults")
        return data

    try:
        with open(path, "r", encoding="utf-8") as f:
            if path.endswith((".yaml", ".yml")):
                user = yaml.safe_load(f) or {}
            else:
                user = json.load(f)
    except (OSError, yaml.YAMLError, json.JSONDecodeError) as e:
        log_warning("CONFIG", f"failed to load {path}: {e}")
        return data

    # Мелкое слияние
    for k, v in user.items():
        if isinstance(v, dict) and isinstance(data.get(k), dict):
            data[k].update(v)
        else:
            data[k] = v
    log_info("CONFIG", f"loaded config from {path}")
    return data