from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.game import (
    Developer,
    Game,
    Publisher,
    Tag,
    game_developers,
    game_publishers,
    game_tags,
)
from app.repositories.game_repo import list_games as list_games_base


def list_tags(db: Session, *, page: int, per_page: int, q: str | None) -> tuple[list[tuple[Tag, int]], int]:
    stmt: Select = (
        select(Tag, func.count(game_tags.c.game_id).label('game_count'))
        .outerjoin(game_tags, game_tags.c.tag_id == Tag.id)
        .group_by(Tag.id)
    )
    count_stmt = select(func.count()).select_from(Tag)
    if q:
        pattern = f'%{q}%'
        stmt = stmt.where(Tag.name.ilike(pattern))
        count_stmt = count_stmt.where(Tag.name.ilike(pattern))

    stmt = stmt.order_by(func.count(game_tags.c.game_id).desc(), Tag.name.asc())
    total = db.scalar(count_stmt) or 0
    offset = (page - 1) * per_page
    rows = list(db.execute(stmt.offset(offset).limit(per_page)).all())
    return rows, total


def get_tag_by_slug(db: Session, slug: str) -> Tag | None:
    return db.scalar(select(Tag).where(Tag.slug == slug))


def get_tag_game_count(db: Session, tag_id: int) -> int:
    return int(db.scalar(select(func.count()).select_from(game_tags).where(game_tags.c.tag_id == tag_id)) or 0)


def list_developers(db: Session, *, page: int, per_page: int, q: str | None) -> tuple[list[tuple[Developer, int]], int]:
    stmt: Select = (
        select(Developer, func.count(game_developers.c.game_id).label('game_count'))
        .outerjoin(game_developers, game_developers.c.developer_id == Developer.id)
        .group_by(Developer.id)
    )
    count_stmt = select(func.count()).select_from(Developer)
    if q:
        pattern = f'%{q}%'
        stmt = stmt.where(Developer.name.ilike(pattern))
        count_stmt = count_stmt.where(Developer.name.ilike(pattern))

    stmt = stmt.order_by(func.count(game_developers.c.game_id).desc(), Developer.name.asc())
    total = db.scalar(count_stmt) or 0
    offset = (page - 1) * per_page
    rows = list(db.execute(stmt.offset(offset).limit(per_page)).all())
    return rows, total


def get_developer_by_slug(db: Session, slug: str) -> Developer | None:
    return db.scalar(select(Developer).where(Developer.slug == slug))


def get_developer_stats(db: Session, developer_id: int) -> tuple[int, float | None]:
    stmt = (
        select(
            func.count(game_developers.c.game_id),
            func.avg(func.nullif(Game.metacritic_score, 0)),
        )
        .select_from(game_developers)
        .join(Game, Game.id == game_developers.c.game_id)
        .where(game_developers.c.developer_id == developer_id)
    )
    count, avg_score = db.execute(stmt).one()
    return int(count or 0), float(avg_score) if avg_score is not None else None


def list_publishers(db: Session, *, page: int, per_page: int) -> tuple[list[tuple[Publisher, int]], int]:
    stmt: Select = (
        select(Publisher, func.count(game_publishers.c.game_id).label('game_count'))
        .outerjoin(game_publishers, game_publishers.c.publisher_id == Publisher.id)
        .group_by(Publisher.id)
        .order_by(func.count(game_publishers.c.game_id).desc(), Publisher.name.asc())
    )
    total = db.scalar(select(func.count()).select_from(Publisher)) or 0
    offset = (page - 1) * per_page
    rows = list(db.execute(stmt.offset(offset).limit(per_page)).all())
    return rows, total


def get_publisher_by_slug(db: Session, slug: str) -> Publisher | None:
    return db.scalar(select(Publisher).where(Publisher.slug == slug))


def get_publisher_game_count(db: Session, publisher_id: int) -> int:
    return int(db.scalar(select(func.count()).select_from(game_publishers).where(game_publishers.c.publisher_id == publisher_id)) or 0)


def list_games_for_tag(
    db: Session,
    *,
    tag: str,
    page: int,
    per_page: int,
    genre: str | None,
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


def list_games_for_developer(db: Session, **kwargs):
    return list_games_base(db, **kwargs)


def list_games_for_publisher(db: Session, **kwargs):
    return list_games_base(db, **kwargs)
