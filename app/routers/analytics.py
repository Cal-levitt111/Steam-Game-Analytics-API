from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.analytics_repo import (
    get_free_vs_paid,
    get_genre_growth,
    get_platform_breakdown,
    get_price_distribution,
    get_release_trends,
    get_review_sentiment,
    get_score_by_genre,
    get_top_developers,
    get_top_genres,
)

router = APIRouter(prefix='/analytics', tags=['analytics'])


def _envelope(data: list[dict[str, object]], query_params: dict[str, object]) -> dict[str, object]:
    return {
        'data': data,
        'generated_at': datetime.now(UTC).isoformat(),
        'query_params': query_params,
    }


@router.get('/release-trends')
def release_trends(
    release_from: date | None = None,
    release_to: date | None = None,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    data = get_release_trends(db, release_from=release_from, release_to=release_to)
    return _envelope(data, {'release_from': release_from, 'release_to': release_to})


@router.get('/top-genres')
def top_genres(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)) -> dict[str, object]:
    data = get_top_genres(db, limit=limit)
    return _envelope(data, {'limit': limit})


@router.get('/genre-growth')
def genre_growth(
    genres: str | None = None,
    from_year: int | None = Query(default=None, alias='from'),
    to_year: int | None = Query(default=None, alias='to'),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    genre_list = [slug.strip() for slug in genres.split(',') if slug.strip()] if genres else None
    data = get_genre_growth(db, genres=genre_list, from_year=from_year, to_year=to_year)
    return _envelope(data, {'genres': genre_list, 'from': from_year, 'to': to_year})


@router.get('/price-distribution')
def price_distribution(db: Session = Depends(get_db)) -> dict[str, object]:
    data = get_price_distribution(db)
    return _envelope(data, {})


@router.get('/top-developers')
def top_developers(
    sort: str = Query(default='game_count', pattern='^(game_count|avg_metacritic_score)$'),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    data = get_top_developers(db, sort=sort, limit=limit)
    return _envelope(data, {'sort': sort, 'limit': limit})


@router.get('/score-by-genre')
def score_by_genre(db: Session = Depends(get_db)) -> dict[str, object]:
    data = get_score_by_genre(db)
    return _envelope(data, {})


@router.get('/free-vs-paid')
def free_vs_paid(db: Session = Depends(get_db)) -> dict[str, object]:
    data = get_free_vs_paid(db)
    return _envelope(data, {})


@router.get('/platform-breakdown')
def platform_breakdown(db: Session = Depends(get_db)) -> dict[str, object]:
    data = get_platform_breakdown(db)
    return _envelope(data, {})


@router.get('/review-sentiment')
def review_sentiment(db: Session = Depends(get_db)) -> dict[str, object]:
    data = get_review_sentiment(db)
    return _envelope(data, {})
