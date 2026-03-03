from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.pagination import build_pagination
from app.schemas.game import SearchGameItem
from app.services.search_service import search_catalog

router = APIRouter(prefix='/search', tags=['search'])


@router.get('')
def search_games(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    genre: str | None = None,
    tag: str | None = None,
    is_free: bool | None = None,
    min_score: int | None = Query(default=None, ge=0, le=100),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    games, total, ranks = search_catalog(
        db,
        q=q,
        page=page,
        per_page=per_page,
        genre=genre,
        tag=tag,
        is_free=is_free,
        min_score=min_score,
    )

    data: list[dict[str, object]] = []
    for game in games:
        item = SearchGameItem.model_validate(game).model_dump()
        item['rank'] = ranks.get(game.id)
        data.append(item)

    pagination = build_pagination(
        page=page,
        per_page=per_page,
        total=total,
        base_path='/api/v1/search',
        query_params={
            'q': q,
            'genre': genre,
            'tag': tag,
            'is_free': is_free,
            'min_score': min_score,
        },
    )

    return {'data': data, 'pagination': pagination}
