from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: object | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class PaginationEnvelope(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    next: str | None
    prev: str | None