from src.devices.disk import Disk


def test_disk_metrics():
    d = Disk()
    m = d.get_metrics()
    assert "disks" in m
    for disk in m["disks"]:
        assert 0 <= disk["percent"] <= 100
        assert disk["total_gb"] > 0