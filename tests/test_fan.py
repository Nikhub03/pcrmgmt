import pytest
from src.devices.fan import Fan
from src.core.errors import InvalidArgument


def test_fan_metrics():
    f = Fan()
    m = f.get_metrics()
    assert len(m["fans"]) >= 1
    assert all("rpm" in fan for fan in m["fans"])


def test_fan_set_speed():
    f = Fan()
    r = f.set_speed(0, 50)
    assert r["speed_percent"] == 50
    assert 500 <= r["rpm"] <= 3000


def test_fan_invalid_speed():
    f = Fan()
    with pytest.raises(InvalidArgument):
        f.set_speed(0, 150)
