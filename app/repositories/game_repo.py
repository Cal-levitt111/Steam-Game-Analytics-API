from datetime import date
from decimal import Decimal

from sqlalchemy import Select, asc, desc, func, or_, select, text
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


def _load_games_by_ids(db: Session, game_ids: list[int]) -> list[Game]:
    if not game_ids:
        return []
    stmt = (
        select(Game)
        .where(Game.id.in_(game_ids))
        .options(
            selectinload(Game.genres),
            selectinload(Game.tags),
            selectinload(Game.categories),
            selectinload(Game.developers),
            selectinload(Game.publishers),
        )
    )
    by_id = {game.id: game for game in db.scalars(stmt).all()}
    return [by_id[game_id] for game_id in game_ids if game_id in by_id]


def search_games(
    db: Session,
    *,
    q: str,
    page: int,
    per_page: int,
    genre: str | None,
    tag: str | None,
    is_free: bool | None,
    min_score: int | None,
) -> tuple[list[Game], int, dict[int, float | None]]:
    offset = (page - 1) * per_page

    if db.bind and db.bind.dialect.name == 'postgresql':
        where_sql = [
            "g.search_vector @@ websearch_to_tsquery('english', :q)",
            "(:genre IS NULL OR EXISTS (SELECT 1 FROM game_genres gg JOIN genres ge ON ge.id = gg.genre_id WHERE gg.game_id = g.id AND ge.slug = :genre))",
            "(:tag IS NULL OR EXISTS (SELECT 1 FROM game_tags gt JOIN tags t ON t.id = gt.tag_id WHERE gt.game_id = g.id AND t.slug = :tag))",
            "(:is_free IS NULL OR g.is_free = :is_free)",
            "(:min_score IS NULL OR g.metacritic_score >= :min_score)",
        ]

        params = {
            'q': q,
            'genre': genre,
            'tag': tag,
            'is_free': is_free,
            'min_score': min_score,
            'limit': per_page,
            'offset': offset,
        }

        count_sql = text(
            f"""
            SELECT COUNT(*)
            FROM games g
            WHERE {' AND '.join(where_sql)}
            """
        )
        total = int(db.execute(count_sql, params).scalar() or 0)

        search_sql = text(
            f"""
            SELECT
                g.id,
                ts_rank(g.search_vector, websearch_to_tsquery('english', :q)) AS rank
            FROM games g
            WHERE {' AND '.join(where_sql)}
            ORDER BY rank DESC, g.id ASC
            LIMIT :limit OFFSET :offset
            """
        )
        rows = db.execute(search_sql, params).all()
        ordered_ids = [int(row[0]) for row in rows]
        rank_map = {int(row[0]): float(row[1]) if row[1] is not None else None for row in rows}
        games = _load_games_by_ids(db, ordered_ids)
        return games, total, rank_map

    pattern = f'%{q}%'
    stmt = (
        select(Game)
        .where(or_(Game.name.ilike(pattern), Game.about_the_game.ilike(pattern)))
        .options(
            selectinload(Game.genres),
            selectinload(Game.tags),
            selectinload(Game.categories),
            selectinload(Game.developers),
            selectinload(Game.publishers),
        )
    )
    stmt = _apply_filters(
        stmt,
        genre=genre,
        tag=tag,
        developer=None,
        publisher=None,
        platform=None,
        is_free=is_free,
        min_price=None,
        max_price=None,
        min_score=min_score,
        release_from=None,
        release_to=None,
    ).distinct()

    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0
    games = list(db.scalars(stmt.order_by(Game.name.asc(), Game.id.asc()).offset(offset).limit(per_page)).all())
    rank_map = {game.id: None for game in games}
    return games, total, rank_map
