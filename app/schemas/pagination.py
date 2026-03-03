from typing import Generic, TypeVar

from pydantic import BaseModel

from app.schemas.common import PaginationEnvelope

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: PaginationEnvelope


class DataResponse(BaseModel, Generic[T]):
    data: T