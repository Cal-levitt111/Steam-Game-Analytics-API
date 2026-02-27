from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.game import GameListItem


class CollectionCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    is_public: bool = False


class CollectionUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    is_public: bool | None = None


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    description: str | None = None
    is_public: bool
    created_at: datetime
    updated_at: datetime


class CollectionListItem(CollectionRead):
    game_count: int = 0


class CollectionDetail(CollectionRead):
    games: list[GameListItem] = []