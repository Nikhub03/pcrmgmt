"""Абстрактные интерфейсы устройств (принцип инверсии зависимостей)."""
from abc import ABC, abstractmethod


class Device(ABC):
    @abstractmethod
    def get_metrics(self) -> dict: ...

    @abstractmethod
    def get_status(self) -> dict: ...