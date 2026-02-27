from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.repositories.game_repo import search_games


def search_catalog(
    db: Session,
    *,
    q: str,
    page: int,
    per_page: int,
    genre: str | None,
    tag: str | None,
    is_free: bool | None,
    min_score: int | None,
):
    if not q.strip():
        raise AppException(400, 'BAD_REQUEST', "Query parameter 'q' is required.")
    return search_games(
        db,
        q=q,
        page=page,
        per_page=per_page,
        genre=genre,
        tag=tag,
        is_free=is_free,
        min_score=min_score,
    )