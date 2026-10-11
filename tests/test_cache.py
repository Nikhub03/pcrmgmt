import time
from src.core.cache import TTLCache


def test_set_get():
    c = TTLCache()
    c.set("k", 42, ttl=1.0)
    assert c.get("k") == 42


def test_expiration():
    c = TTLCache()
    c.set("k", "v", ttl=0.05)
    time.sleep(0.1)
    assert c.get("k") is None


def test_lru_eviction():
    c = TTLCache(max_items=3)
    c.set("a", 1, ttl=10)
    c.set("b", 2, ttl=10)
    c.set("c", 3, ttl=10)
    c.set("d", 4, ttl=10)
    assert c.size() <= 3