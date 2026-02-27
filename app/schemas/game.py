from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class NamedSlug(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class GameListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    steam_app_id: int
    name: str
    release_date: date | None = None
    price_usd: Decimal | None = None
    is_free: bool
    metacritic_score: int | None = None
    positive_reviews: int
    negative_reviews: int
    windows: bool
    mac: bool
    linux: bool


class GameDetail(GameListItem):
    short_description: str | None = None
    detailed_description: str | None = None
    required_age: int
    website: str | None = None
    header_image: str | None = None
    created_at: datetime

    genres: list[NamedSlug] = []
    tags: list[NamedSlug] = []
    categories: list[NamedSlug] = []
    developers: list[NamedSlug] = []
    publishers: list[NamedSlug] = []