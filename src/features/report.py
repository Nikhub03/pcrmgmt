"""Генерация HTML-отчёта с графиками (matplotlib → Base64)."""
import base64
import io
import json
import random
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ..core.logger import log_info


def _simulate_series(n=60, seed=42):
    rng = random.Random(seed)
    base = datetime.now() - timedelta(minutes=n)
    cpu, ram, temp = [], [], []
    for i in range(n):
        cpu.append(rng.randint(5, 85))
        ram.append(rng.randint(40, 80))
        temp.append(rng.randint(35, 75))
    return {
        "timestamps": [(base + timedelta(minutes=i)).strftime("%H:%M")
                       for i in range(n)],
        "cpu": cpu, "ram": ram, "temp": temp,
    }


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _line_chart(x, y1, y2, title, label1, label2):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y1, label=label1, marker="o", markersize=3)
    ax.plot(x, y2, label=label2, marker="s", markersize=3)
    ax.set_title(title)
    ax.set_xlabel("Время")
    ax.set_ylabel("%")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    return _fig_to_base64(fig)


def _bar_chart(labels, values, title, ylabel):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values, color="#4c72b0")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    return _fig_to_base64(fig)


def generate_report(output_html: str, export_json: str | None = None) -> str:
    data = _simulate_series()
    img_cpu = _line_chart(data["timestamps"], data["cpu"], data["ram"],
                          "CPU / RAM, %", "CPU", "RAM")
    img_temp = _line_chart(data["timestamps"], data["temp"],
                           [0] * len(data["temp"]),
                           "Температура CPU, °C", "CPU", "")
    img_disk = _bar_chart(["C:", "D:"], [72, 45],
                          "Использование дисков, %", "%")

    html = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<title>Отчёт pcrmgmt</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;margin:2em;}}
h1,h2{{color:#2c3e50;}}
img{{max-width:100%;border:1px solid #ddd;border-radius:6px;margin:.5em 0;}}
</style></head><body>
<h1>Отчёт мониторинга</h1>
<p>Сформирован: {datetime.now():%Y-%m-%d %H:%M:%S}</p>
<h2>Загрузка CPU и RAM</h2><img src="data:image/png;base64,{img_cpu}"/>
<h2>Температура CPU</h2><img src="data:image/png;base64,{img_temp}"/>
<h2>Использование дисков</h2><img src="data:image/png;base64,{img_disk}"/>
</body></html>"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)

    if export_json:
        with open(export_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    log_info("REPORT", f"generated {output_html}")
    return output_html