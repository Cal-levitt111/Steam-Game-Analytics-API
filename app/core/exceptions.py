class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        detail: object | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.detail = detail
        self.headers = headers or {}
        super().__init__(message)
