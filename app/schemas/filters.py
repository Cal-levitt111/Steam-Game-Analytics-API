from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class SortOrder(StrEnum):
    asc = 'asc'
    desc = 'desc'


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class GameFilterParams(PaginationParams):
    genre: str | None = None
    tag: str | None = None
    developer: str | None = None
    publisher: str | None = None
    platform: str | None = None
    is_free: bool | None = None
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
    min_score: int | None = Field(default=None, ge=0, le=100)
    release_from: date | None = None
    release_to: date | None = None
    sort: str | None = None
    order: SortOrder = SortOrder.asc


class SearchParams(PaginationParams):
    q: str = Field(min_length=1)
    genre: str | None = None
    tag: str | None = None
    is_free: bool | None = None
    min_score: int | None = Field(default=None, ge=0, le=100)