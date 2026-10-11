import json
from src.features.report import generate_report, _simulate_series


def test_simulate_series():
    s = _simulate_series(n=10)
    assert len(s["cpu"]) == 10
    assert len(s["timestamps"]) == 10


def test_generate_report(tmp_path):
    html = tmp_path / "r.html"
    js = tmp_path / "r.json"
    generate_report(str(html), str(js))
    assert html.exists()
    assert js.exists()
    data = json.loads(js.read_text(encoding="utf-8"))
    assert "cpu" in data
