from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.game import Game, Genre, game_genres


def _year_expr(db: Session):
    if db.bind and db.bind.dialect.name == 'postgresql':
        return func.extract('year', Game.release_date)
    return func.strftime('%Y', Game.release_date)


def get_release_trends(db: Session, *, release_from: date | None, release_to: date | None) -> list[dict[str, int]]:
    year_expr = _year_expr(db)
    stmt = select(year_expr.label('year'), func.count(Game.id).label('game_count')).where(Game.release_date.is_not(None))

    if release_from:
        stmt = stmt.where(Game.release_date >= release_from)
    if release_to:
        stmt = stmt.where(Game.release_date <= release_to)

    stmt = stmt.group_by(year_expr).order_by(year_expr.asc())
    rows = db.execute(stmt).all()
    return [{'year': int(float(year)), 'game_count': int(game_count)} for year, game_count in rows if year is not None]


def get_top_genres(db: Session, *, limit: int) -> list[dict[str, object]]:
    stmt = (
        select(Genre.name, Genre.slug, func.count(game_genres.c.game_id).label('game_count'))
        .outerjoin(game_genres, game_genres.c.genre_id == Genre.id)
        .group_by(Genre.id)
        .order_by(func.count(game_genres.c.game_id).desc(), Genre.name.asc())
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    return [
        {'name': name, 'slug': slug, 'game_count': int(game_count)}
        for name, slug, game_count in rows
    ]


def get_genre_growth(
    db: Session,
    *,
    genres: list[str] | None,
    from_year: int | None,
    to_year: int | None,
) -> list[dict[str, object]]:
    year_expr = _year_expr(db)
    stmt = (
        select(Genre.slug, year_expr.label('year'), func.count(Game.id).label('game_count'))
        .join(game_genres, game_genres.c.genre_id == Genre.id)
        .join(Game, Game.id == game_genres.c.game_id)
        .where(Game.release_date.is_not(None))
    )

    conditions = []
    if genres:
        conditions.append(Genre.slug.in_(genres))
    if from_year is not None:
        conditions.append(year_expr >= from_year)
    if to_year is not None:
        conditions.append(year_expr <= to_year)
    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.group_by(Genre.slug, year_expr).order_by(Genre.slug.asc(), year_expr.asc())
    rows = db.execute(stmt).all()
    return [
        {'slug': slug, 'year': int(float(year)), 'game_count': int(game_count)}
        for slug, year, game_count in rows
        if year is not None
    ]