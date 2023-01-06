class BaseBunnyNetStorageException(Exception):
    pass


class EmptyParameter(BaseBunnyNetStorageException, ValueError):
    pass


class NetworkException(BaseBunnyNetStorageException):
    pass


class StatusCodeException(NetworkException):
    def __init__(self, status_code: int):
        self.status_code = status_code
