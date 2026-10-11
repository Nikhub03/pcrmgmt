"""Простой веб-интерфейс на Flask."""
from flask import Flask, jsonify, render_template_string
from ..core.logger import log_info
from ..devices.cpu import CPU
from ..devices.ram import RAM
from ..devices.disk import Disk
from ..devices.gpu import GPU

cpu, ram, disk, gpu = CPU(), RAM(), Disk(), GPU()

PAGE = """<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><title>pcrmgmt</title>
<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:2em;background:#f7f7fa;}
table{border-collapse:collapse;background:#fff;}
td,th{border:1px solid #ccc;padding:.5em 1em;}
th{background:#eaeaea;}
</style>
<script>
async function refresh(){
  const r = await fetch('/api/metrics');
  const d = await r.json();
  document.getElementById('cpu').textContent = d.cpu.load_percent + ' %';
  document.getElementById('cpu_t').textContent = d.cpu.temperature_c + ' °C';
  document.getElementById('ram').textContent = d.ram.percent + ' %';
  document.getElementById('gpu').textContent = d.gpu.load_percent + ' %';
}
setInterval(refresh, 2000); refresh();
</script></head>
<body>
<h1>pcrmgmt — мониторинг</h1>
<table>
<tr><th>Метрика</th><th>Значение</th></tr>
<tr><td>CPU</td><td id="cpu">—</td></tr>
<tr><td>CPU темп.</td><td id="cpu_t">—</td></tr>
<tr><td>RAM</td><td id="ram">—</td></tr>
<tr><td>GPU</td><td id="gpu">—</td></tr>
</table>
<p><a href="/api/metrics">/api/metrics (JSON)</a></p>
</body></html>"""


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template_string(PAGE)

    @app.route("/api/metrics")
    def metrics():
        return jsonify({
            "cpu": cpu.get_metrics(),
            "ram": ram.get_metrics(),
            "disks": disk.get_metrics(),
            "gpu": gpu.get_metrics(),
        })

    return app


def run_web(port: int = 8080):
    app = create_app()
    log_info("WEB", f"starting web server on port {port}")
    try:
        app.run(host="127.0.0.1", port=port, debug=False)
    except OSError as e:
        log_info("WEB", f"port {port} busy: {e}")
        print(f"Port {port} is busy. Try another port.")