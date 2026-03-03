from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.pagination import build_pagination
from app.repositories.taxonomy_repo import get_developer_stats, list_developers, list_games_for_developer
from app.schemas.game import GameListItem
from app.services.taxonomy_service import get_developer_or_404

router = APIRouter(prefix='/developers', tags=['developers'])


@router.get('')
def list_developers_route(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    q: str | None = None,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    rows, total = list_developers(db, page=page, per_page=per_page, q=q)
    data = [
        {'id': developer.id, 'name': developer.name, 'slug': developer.slug, 'game_count': int(game_count)}
        for developer, game_count in rows
    ]
    pagination = build_pagination(
        page=page,
        per_page=per_page,
        total=total,
        base_path='/api/v1/developers',
        query_params={'q': q},
    )
    return {'data': data, 'pagination': pagination}


@router.get('/{slug}')
def get_developer_detail(slug: str, db: Session = Depends(get_db)) -> dict[str, object]:
    developer = get_developer_or_404(db, slug)
    game_count, avg_metacritic_score = get_developer_stats(db, developer.id)
    return {
        'data': {
            'id': developer.id,
            'name': developer.name,
            'slug': developer.slug,
            'game_count': game_count,
            'avg_metacritic_score': avg_metacritic_score,
        }
    }


@router.get('/{slug}/games')
def list_developer_games(
    slug: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    genre: str | None = None,
    tag: str | None = None,
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
    get_developer_or_404(db, slug)
    games, total = list_games_for_developer(
        db,
        page=page,
        per_page=per_page,
        genre=genre,
        tag=tag,
        developer=slug,
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
        base_path=f'/api/v1/developers/{slug}/games',
        query_params={
            'genre': genre,
            'tag': tag,
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