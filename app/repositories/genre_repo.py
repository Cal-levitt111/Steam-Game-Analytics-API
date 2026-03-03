from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.game import Game, Genre, game_genres
from app.repositories.game_repo import list_games as list_games_base


def list_genres(db: Session, *, page: int, per_page: int) -> tuple[list[tuple[Genre, int]], int]:
    stmt: Select = (
        select(Genre, func.count(game_genres.c.game_id).label('game_count'))
        .outerjoin(game_genres, game_genres.c.genre_id == Genre.id)
        .group_by(Genre.id)
        .order_by(func.count(game_genres.c.game_id).desc(), Genre.name.asc())
    )

    total = db.scalar(select(func.count()).select_from(Genre)) or 0
    offset = (page - 1) * per_page
    rows = list(db.execute(stmt.offset(offset).limit(per_page)).all())
    return rows, total


def get_genre_by_slug(db: Session, slug: str) -> Genre | None:
    return db.scalar(select(Genre).where(Genre.slug == slug))


def get_genre_game_count(db: Session, genre_id: int) -> int:
    stmt = select(func.count()).select_from(game_genres).where(game_genres.c.genre_id == genre_id)
    return int(db.scalar(stmt) or 0)


def get_top_games_for_genre(db: Session, genre_slug: str, limit: int = 10) -> list[Game]:
    stmt = (
        select(Game)
        .join(Game.genres)
        .where(Genre.slug == genre_slug)
        .order_by(Game.positive_reviews.desc(), Game.id.asc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def list_games_for_genre(
    db: Session,
    *,
    genre: str,
    page: int,
    per_page: int,
    tag: str | None,
    developer: str | None,
    publisher: str | None,
    platform: str | None,
    is_free: bool | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    min_score: int | None,
    release_from,
    release_to,
    sort: str | None,
    order: str,
):
    return list_games_base(
        db,
        page=page,
        per_page=per_page,
        genre=genre,
        tag=tag,
        developer=developer,
        publisher=publisher,
        platform=platform,
        is_free=is_free,
        min_price=min_price,
        max_price=max_price,
        min_score=min_score,
        release_from=release_from,
        release_to=release_to,
        sort=sort,
        order=order,
    )