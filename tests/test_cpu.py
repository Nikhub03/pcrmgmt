from src.devices.cpu import CPU


def test_cpu_metrics():
    cpu = CPU()
    m = cpu.get_metrics()
    assert "model" in m
    assert 0 <= m["load_percent"] <= 100
    assert m["temperature_c"] > 0


def test_cpu_cache():
    cpu = CPU()
    a = cpu.get_metrics()
    b = cpu.get_metrics()
    assert a == b