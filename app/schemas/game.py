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
    about_the_game: str | None = None
    required_age: int
    estimated_owners: str | None = None
    peak_ccu: int | None = None
    discount_percent: int | None = None
    dlc_count: int | None = None
    supported_languages: str | None = None
    full_audio_languages: str | None = None
    reviews: str | None = None
    website: str | None = None
    support_url: str | None = None
    support_email: str | None = None
    header_image: str | None = None
    metacritic_url: str | None = None
    user_score: int | None = None
    score_rank: str | None = None
    achievements: int | None = None
    recommendations: int | None = None
    notes: str | None = None
    average_playtime_forever: int | None = None
    average_playtime_two_weeks: int | None = None
    median_playtime_forever: int | None = None
    median_playtime_two_weeks: int | None = None
    screenshots: str | None = None
    movies: str | None = None
    created_at: datetime

    genres: list[NamedSlug] = []
    tags: list[NamedSlug] = []
    categories: list[NamedSlug] = []
    developers: list[NamedSlug] = []
    publishers: list[NamedSlug] = []


class SearchGameItem(GameListItem):
    rank: float | None = None
