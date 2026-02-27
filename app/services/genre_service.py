from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.repositories import genre_repo


def get_genre_or_404(db: Session, slug: str):
    genre = genre_repo.get_genre_by_slug(db, slug)
    if genre is None:
        raise AppException(404, 'RESOURCE_NOT_FOUND', f'Genre with slug {slug} was not found.')
    return genre