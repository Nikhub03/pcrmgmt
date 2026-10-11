"""Потокобезопасный TTL-кэш с ленивой инвалидацией."""
import threading
import time


class TTLCache:
    def __init__(self, max_items: int = 1000):
        self._store = {}
        self._lock = threading.RLock()
        self._max = max_items

    def get(self, key):
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            value, expire_at = item
            if time.time() > expire_at:
                self._store.pop(key, None)
                return None
            return value

    def set(self, key, value, ttl: float):
        with self._lock:
            if len(self._store) >= self._max:
                # LRU-подобное вытеснение: удаляем самый старый
                oldest = min(self._store, key=lambda k: self._store[k][1])
                self._store.pop(oldest, None)
            self._store[key] = (value, time.time() + ttl)

    def clear(self):
        with self._lock:
            self._store.clear()

    def size(self):
        with self._lock:
            return len(self._store)


CACHE = TTLCache()