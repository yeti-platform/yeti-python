class YetiError(RuntimeError):
    """Base class for errors in the Yeti package."""


class YetiApiError(YetiError):
    """Base class for errors in the Yeti API."""

    status_code: int
    message: str

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


class YetiAuthError(YetiError):
    """Error authenticating with the Yeti API."""

    def __init__(self, message: str):
        super().__init__(message)
