from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.pagination import build_pagination
from app.repositories.genre_repo import get_genre_game_count, get_top_games_for_genre, list_games_for_genre, list_genres
from app.schemas.game import GameListItem
from app.services.genre_service import get_genre_or_404

router = APIRouter(prefix='/genres', tags=['genres'])


@router.get('')
def list_genres_route(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    rows, total = list_genres(db, page=page, per_page=per_page)
    data = [
        {
            'id': genre.id,
            'name': genre.name,
            'slug': genre.slug,
            'game_count': int(game_count),
        }
        for genre, game_count in rows
    ]
    pagination = build_pagination(
        page=page,
        per_page=per_page,
        total=total,
        base_path='/api/v1/genres',
        query_params={},
    )
    return {'data': data, 'pagination': pagination}


@router.get('/{slug}')
def get_genre_detail(slug: str, db: Session = Depends(get_db)) -> dict[str, object]:
    genre = get_genre_or_404(db, slug)
    game_count = get_genre_game_count(db, genre.id)
    top_games = [GameListItem.model_validate(game).model_dump() for game in get_top_games_for_genre(db, slug, limit=10)]
    return {
        'data': {
            'id': genre.id,
            'name': genre.name,
            'slug': genre.slug,
            'game_count': game_count,
            'top_games': top_games,
        }
    }


@router.get('/{slug}/games')
def list_genre_games(
    slug: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    tag: str | None = None,
    developer: str | None = None,
    publisher: str | None = None,
    platform: str | None = Query(default=None, pattern='^(windows|mac|linux)$'),
    is_free: bool | None = None,
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    min_score: int | None = Query(default=None, ge=0, le=100),
    release_from: date | None = None,
    release_to: date | None = None,
    sort: str | None = Query(default='name'),
    order: str = Query(default='asc', pattern='^(asc|desc)$'),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    get_genre_or_404(db, slug)
    games, total = list_games_for_genre(
        db,
        genre=slug,
        page=page,
        per_page=per_page,
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
    data = [GameListItem.model_validate(game).model_dump() for game in games]
    pagination = build_pagination(
        page=page,
        per_page=per_page,
        total=total,
        base_path=f'/api/v1/genres/{slug}/games',
        query_params={
            'tag': tag,
            'developer': developer,
            'publisher': publisher,
            'platform': platform,
            'is_free': is_free,
            'min_price': min_price,
            'max_price': max_price,
            'min_score': min_score,
            'release_from': release_from,
            'release_to': release_to,
            'sort': sort,
            'order': order,
        },
    )
    return {'data': data, 'pagination': pagination}