from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.analytics_repo import get_genre_growth, get_release_trends, get_top_genres

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