from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.pagination import build_pagination
from app.repositories.taxonomy_repo import get_publisher_game_count, list_games_for_publisher, list_publishers
from app.schemas.game import GameListItem
from app.services.taxonomy_service import get_publisher_or_404

router = APIRouter(prefix='/publishers', tags=['publishers'])


@router.get('')
def list_publishers_route(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    rows, total = list_publishers(db, page=page, per_page=per_page)
    data = [
        {'id': publisher.id, 'name': publisher.name, 'slug': publisher.slug, 'game_count': int(game_count)}
        for publisher, game_count in rows
    ]
    pagination = build_pagination(
        page=page,
        per_page=per_page,
        total=total,
        base_path='/api/v1/publishers',
        query_params={},
    )
    return {'data': data, 'pagination': pagination}


@router.get('/{slug}')
def get_publisher_detail(slug: str, db: Session = Depends(get_db)) -> dict[str, object]:
    publisher = get_publisher_or_404(db, slug)
    game_count = get_publisher_game_count(db, publisher.id)
    return {
        'data': {
            'id': publisher.id,
            'name': publisher.name,
            'slug': publisher.slug,
            'game_count': game_count,
        }
    }


@router.get('/{slug}/games')
def list_publisher_games(
    slug: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    genre: str | None = None,
    tag: str | None = None,
    developer: str | None = None,
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
    get_publisher_or_404(db, slug)
    games, total = list_games_for_publisher(
        db,
        page=page,
        per_page=per_page,
        genre=genre,
        tag=tag,
        developer=developer,
        publisher=slug,
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
        base_path=f'/api/v1/publishers/{slug}/games',
        query_params={
            'genre': genre,
            'tag': tag,
            'developer': developer,
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