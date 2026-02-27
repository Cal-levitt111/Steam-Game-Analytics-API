class AppException(Exception):
    def __init__(self, status_code: int, code: str, message: str, detail: object | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)