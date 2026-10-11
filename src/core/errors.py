class PCRMError(Exception):
    """Базовая ошибка приложения."""


class DeviceNotFound(PCRMError):
    pass


class PermissionDenied(PCRMError):
    pass


class InvalidArgument(PCRMError):
    pass