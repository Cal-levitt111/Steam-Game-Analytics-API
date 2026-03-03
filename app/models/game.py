from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Table, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


game_genres = Table(
    'game_genres',
    Base.metadata,
    Column('game_id', ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True),
)

game_tags = Table(
    'game_tags',
    Base.metadata,
    Column('game_id', ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)

game_categories = Table(
    'game_categories',
    Base.metadata,
    Column('game_id', ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True),
)

game_developers = Table(
    'game_developers',
    Base.metadata,
    Column('game_id', ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('developer_id', ForeignKey('developers.id', ondelete='CASCADE'), primary_key=True),
)

game_publishers = Table(
    'game_publishers',
    Base.metadata,
    Column('game_id', ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('publisher_id', ForeignKey('publishers.id', ondelete='CASCADE'), primary_key=True),
)


class Game(Base):
    __tablename__ = 'games'

    id: Mapped[int] = mapped_column(primary_key=True)
    steam_app_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date)
    estimated_owners: Mapped[str | None] = mapped_column(Text)
    peak_ccu: Mapped[int | None] = mapped_column(Integer)
    price_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    discount_percent: Mapped[int | None] = mapped_column(SmallInteger)
    dlc_count: Mapped[int | None] = mapped_column(Integer)
    about_the_game: Mapped[str | None] = mapped_column(Text)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supported_languages: Mapped[str | None] = mapped_column(Text)
    full_audio_languages: Mapped[str | None] = mapped_column(Text)
    reviews: Mapped[str | None] = mapped_column(Text)
    support_url: Mapped[str | None] = mapped_column(Text)
    support_email: Mapped[str | None] = mapped_column(Text)
    metacritic_score: Mapped[int | None] = mapped_column(SmallInteger)
    metacritic_url: Mapped[str | None] = mapped_column(Text)
    user_score: Mapped[int | None] = mapped_column(Integer)
    positive_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    negative_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score_rank: Mapped[str | None] = mapped_column(Text)
    achievements: Mapped[int | None] = mapped_column(Integer)
    recommendations: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    average_playtime_forever: Mapped[int | None] = mapped_column(Integer)
    average_playtime_two_weeks: Mapped[int | None] = mapped_column(Integer)
    median_playtime_forever: Mapped[int | None] = mapped_column(Integer)
    median_playtime_two_weeks: Mapped[int | None] = mapped_column(Integer)
    required_age: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    website: Mapped[str | None] = mapped_column(Text)
    header_image: Mapped[str | None] = mapped_column(Text)
    windows: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mac: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    linux: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    screenshots: Mapped[str | None] = mapped_column(Text)
    movies: Mapped[str | None] = mapped_column(Text)
    search_vector = mapped_column(TSVECTOR)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    genres: Mapped[list[Genre]] = relationship(secondary=game_genres, back_populates='games')
    tags: Mapped[list[Tag]] = relationship(secondary=game_tags, back_populates='games')
    categories: Mapped[list[Category]] = relationship(secondary=game_categories, back_populates='games')
    developers: Mapped[list[Developer]] = relationship(secondary=game_developers, back_populates='games')
    publishers: Mapped[list[Publisher]] = relationship(secondary=game_publishers, back_populates='games')


class Developer(Base):
    __tablename__ = 'developers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    games: Mapped[list[Game]] = relationship(secondary=game_developers, back_populates='developers')


class Publisher(Base):
    __tablename__ = 'publishers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    games: Mapped[list[Game]] = relationship(secondary=game_publishers, back_populates='publishers')


class Genre(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    games: Mapped[list[Game]] = relationship(secondary=game_genres, back_populates='genres')


class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    games: Mapped[list[Game]] = relationship(secondary=game_tags, back_populates='tags')


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    games: Mapped[list[Game]] = relationship(secondary=game_categories, back_populates='categories')
