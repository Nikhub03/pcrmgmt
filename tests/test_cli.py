import subprocess
import sys
import json


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "src.main", *args],
        capture_output=True, text=True, timeout=30
    )


def test_help():
    r = _run("help")
    assert r.returncode == 0
    assert "status" in r.stdout


def test_status():
    r = _run("status")
    assert r.returncode == 0
    assert "CPU" in r.stdout


def test_info_json():
    r = _run("info", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "cpu" in data and "ram" in data


def test_monitor_bad_interval():
    r = _run("monitor", "--interval", "-1")
    assert r.returncode == 2
    assert "Invalid value" in r.stderr or "Invalid value" in r.stdout