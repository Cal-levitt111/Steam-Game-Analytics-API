from datetime import date
from decimal import Decimal

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.game import Developer, Game, Genre, Publisher, Tag

SORT_FIELD_MAP = {
    'name': Game.name,
    'price_usd': Game.price_usd,
    'metacritic_score': Game.metacritic_score,
    'release_date': Game.release_date,
    'positive_reviews': Game.positive_reviews,
}


def _apply_filters(
    stmt: Select[tuple[Game]],
    *,
    genre: str | None,
    tag: str | None,
    developer: str | None,
    publisher: str | None,
    platform: str | None,
    is_free: bool | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    min_score: int | None,
    release_from: date | None,
    release_to: date | None,
) -> Select[tuple[Game]]:
    if genre:
        stmt = stmt.join(Game.genres).where(Genre.slug == genre)
    if tag:
        stmt = stmt.join(Game.tags).where(Tag.slug == tag)
    if developer:
        stmt = stmt.join(Game.developers).where(Developer.slug == developer)
    if publisher:
        stmt = stmt.join(Game.publishers).where(Publisher.slug == publisher)

    if platform in {'windows', 'mac', 'linux'}:
        stmt = stmt.where(getattr(Game, platform).is_(True))

    if is_free is not None:
        stmt = stmt.where(Game.is_free.is_(is_free))
    if min_price is not None:
        stmt = stmt.where(Game.price_usd >= min_price)
    if max_price is not None:
        stmt = stmt.where(Game.price_usd <= max_price)
    if min_score is not None:
        stmt = stmt.where(Game.metacritic_score >= min_score)
    if release_from is not None:
        stmt = stmt.where(Game.release_date >= release_from)
    if release_to is not None:
        stmt = stmt.where(Game.release_date <= release_to)

    return stmt


def list_games(
    db: Session,
    *,
    page: int,
    per_page: int,
    genre: str | None,
    tag: str | None,
    developer: str | None,
    publisher: str | None,
    platform: str | None,
    is_free: bool | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    min_score: int | None,
    release_from: date | None,
    release_to: date | None,
    sort: str | None,
    order: str,
) -> tuple[list[Game], int]:
    stmt = select(Game).options(
        selectinload(Game.genres),
        selectinload(Game.tags),
        selectinload(Game.categories),
        selectinload(Game.developers),
        selectinload(Game.publishers),
    )

    stmt = _apply_filters(
        stmt,
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
    ).distinct()

    sort_column = SORT_FIELD_MAP.get(sort or '', Game.name)
    stmt = stmt.order_by(desc(sort_column) if order == 'desc' else asc(sort_column), Game.id.asc())

    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0

    offset = (page - 1) * per_page
    games = list(db.scalars(stmt.offset(offset).limit(per_page)).all())
    return games, total


def get_game_by_id(db: Session, game_id: int) -> Game | None:
    stmt = (
        select(Game)
        .where(Game.id == game_id)
        .options(
            selectinload(Game.genres),
            selectinload(Game.tags),
            selectinload(Game.categories),
            selectinload(Game.developers),
            selectinload(Game.publishers),
        )
    )
    return db.scalar(stmt)