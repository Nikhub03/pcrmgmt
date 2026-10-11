from src.devices.ram import RAM


def test_ram_metrics():
    r = RAM()
    m = r.get_metrics()
    assert m["total_gb"] > 0
    assert 0 <= m["percent"] <= 100
    assert m["used_gb"] <= m["total_gb"]