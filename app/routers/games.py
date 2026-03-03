from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.pagination import build_pagination
from app.schemas.game import GameDetail, GameListItem, SimilarGameItem
from app.services.game_service import get_game_or_404, list_games, list_similar_games

router = APIRouter(prefix='/games', tags=['games'])


@router.get('')
def list_games_route(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    genre: str | None = None,
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
    games, total = list_games(
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

    data = [GameListItem.model_validate(game).model_dump() for game in games]
    pagination = build_pagination(
        page=page,
        per_page=per_page,
        total=total,
        base_path='/api/v1/games',
        query_params={
            'genre': genre,
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


@router.get('/{game_id}', response_model=GameDetail)
def get_game_detail(game_id: int, db: Session = Depends(get_db)) -> GameDetail:
    game = get_game_or_404(db, game_id)
    return GameDetail.model_validate(game)


@router.get('/{game_id}/similar')
def get_similar_games_route(
    game_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    games, similarity_map = list_similar_games(db, game_id=game_id, limit=limit)

    data: list[dict[str, object]] = []
    for game in games:
        item = SimilarGameItem.model_validate(game).model_dump()
        item['similarity'] = similarity_map.get(game.id)
        data.append(item)
    return {'data': data}
