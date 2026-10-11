from src.devices.gpu import GPU


def test_gpu_metrics():
    g = GPU()
    m = g.get_metrics()
    assert m["model"]
    assert 0 <= m["load_percent"] <= 100
    assert m["simulated"] is True


def test_gpu_status():
    g = GPU()
    s = g.get_status()
    assert "gpu_load" in s and "gpu_temp" in s
