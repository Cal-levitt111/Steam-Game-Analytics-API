from datetime import date

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from app.models.game import Developer, Game, Genre, game_developers, game_genres


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


def get_price_distribution(db: Session) -> list[dict[str, object]]:
    bucket = case(
        (Game.is_free.is_(True), 'Free'),
        (Game.price_usd < 5, '<5'),
        (Game.price_usd < 15, '5-15'),
        (Game.price_usd < 30, '15-30'),
        (Game.price_usd < 60, '30-60'),
        else_='60+',
    ).label('bucket')

    stmt = select(bucket, func.count(Game.id).label('count')).group_by(bucket)
    rows = db.execute(stmt).all()
    total = sum(int(count) for _, count in rows) or 1
    order = {'Free': 0, '<5': 1, '5-15': 2, '15-30': 3, '30-60': 4, '60+': 5}

    data = []
    for bucket_name, count in rows:
        count_int = int(count)
        data.append(
            {
                'bucket': bucket_name,
                'count': count_int,
                'pct': round((count_int / total) * 100, 2),
            }
        )
    return sorted(data, key=lambda row: order.get(str(row['bucket']), 999))


def get_top_developers(db: Session, *, sort: str, limit: int) -> list[dict[str, object]]:
    avg_score = func.avg(func.nullif(Game.metacritic_score, 0)).label('avg_metacritic_score')
    game_count = func.count(game_developers.c.game_id).label('game_count')
    stmt = (
        select(Developer.name, Developer.slug, game_count, avg_score)
        .outerjoin(game_developers, game_developers.c.developer_id == Developer.id)
        .outerjoin(Game, Game.id == game_developers.c.game_id)
        .group_by(Developer.id)
    )
    if sort == 'avg_metacritic_score':
        stmt = stmt.order_by(avg_score.desc().nullslast(), game_count.desc(), Developer.name.asc())
    else:
        stmt = stmt.order_by(game_count.desc(), avg_score.desc().nullslast(), Developer.name.asc())
    rows = db.execute(stmt.limit(limit)).all()
    return [
        {
            'name': name,
            'slug': slug,
            'game_count': int(count),
            'avg_metacritic_score': float(score) if score is not None else None,
        }
        for name, slug, count, score in rows
    ]


def get_score_by_genre(db: Session) -> list[dict[str, object]]:
    sentiment_ratio = (
        func.nullif(Game.positive_reviews, 0)
        / func.nullif(Game.positive_reviews + Game.negative_reviews, 0)
    )
    stmt = (
        select(
            Genre.name,
            Genre.slug,
            func.avg(func.nullif(Game.metacritic_score, 0)).label('avg_score'),
            func.avg(sentiment_ratio).label('avg_sentiment'),
            func.count(Game.id).label('game_count'),
        )
        .join(game_genres, game_genres.c.genre_id == Genre.id)
        .join(Game, Game.id == game_genres.c.game_id)
        .group_by(Genre.id)
        .order_by(func.avg(func.nullif(Game.metacritic_score, 0)).desc().nullslast(), Genre.name.asc())
    )
    rows = db.execute(stmt).all()
    return [
        {
            'name': name,
            'slug': slug,
            'avg_score': float(avg_score) if avg_score is not None else None,
            'avg_sentiment': float(avg_sentiment) if avg_sentiment is not None else None,
            'game_count': int(game_count),
        }
        for name, slug, avg_score, avg_sentiment, game_count in rows
    ]


def get_free_vs_paid(db: Session) -> list[dict[str, object]]:
    stmt = (
        select(
            Game.is_free,
            func.count(Game.id).label('game_count'),
            func.avg(func.nullif(Game.metacritic_score, 0)).label('avg_score'),
            func.avg(Game.positive_reviews + Game.negative_reviews).label('avg_reviews'),
        )
        .group_by(Game.is_free)
        .order_by(Game.is_free.desc())
    )
    rows = db.execute(stmt).all()
    return [
        {
            'type': 'free' if is_free else 'paid',
            'game_count': int(game_count),
            'avg_score': float(avg_score) if avg_score is not None else None,
            'avg_reviews': float(avg_reviews) if avg_reviews is not None else None,
        }
        for is_free, game_count, avg_score, avg_reviews in rows
    ]


def get_platform_breakdown(db: Session) -> list[dict[str, object]]:
    stmt = select(
        func.count(Game.id).label('total_games'),
        func.sum(case((Game.windows.is_(True), 1), else_=0)).label('windows'),
        func.sum(case((Game.mac.is_(True), 1), else_=0)).label('mac'),
        func.sum(case((Game.linux.is_(True), 1), else_=0)).label('linux'),
        func.sum(case((and_(Game.windows.is_(True), Game.mac.is_(True)), 1), else_=0)).label('windows_mac'),
        func.sum(case((and_(Game.windows.is_(True), Game.linux.is_(True)), 1), else_=0)).label('windows_linux'),
        func.sum(case((and_(Game.mac.is_(True), Game.linux.is_(True)), 1), else_=0)).label('mac_linux'),
        func.sum(
            case(
                (and_(Game.windows.is_(True), Game.mac.is_(True), Game.linux.is_(True)), 1),
                else_=0,
            )
        ).label('all_three'),
    )
    row = db.execute(stmt).one()
    keys = [
        'total_games',
        'windows',
        'mac',
        'linux',
        'windows_mac',
        'windows_linux',
        'mac_linux',
        'all_three',
    ]
    return [{key: int(value or 0) for key, value in zip(keys, row)}]


def get_review_sentiment(db: Session) -> list[dict[str, object]]:
    rows = db.execute(
        select(Game.positive_reviews, Game.negative_reviews).where((Game.positive_reviews + Game.negative_reviews) > 0)
    ).all()
    total = len(rows) or 1
    buckets = [0] * 10
    for positive, negative in rows:
        ratio = positive / (positive + negative)
        index = min(int(ratio * 10), 9)
        buckets[index] += 1

    data = []
    for index, count in enumerate(buckets):
        start = index * 10
        end = (index + 1) * 10
        data.append(
            {
                'bucket': f'{start}-{end}%',
                'count': count,
                'pct': round((count / total) * 100, 2),
            }
        )
    return data
