from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.collection import Collection
from app.models.user import User
from app.repositories import collection_repo


def create_collection(db: Session, *, user: User, name: str, description: str | None, is_public: bool) -> Collection:
    collection = collection_repo.create_collection(
        db,
        user_id=user.id,
        name=name,
        description=description,
        is_public=is_public,
    )
    db.commit()
    return collection


def get_collection_or_404(db: Session, collection_id: int, include_games: bool = False) -> Collection:
    collection = collection_repo.get_collection_by_id(db, collection_id, include_games=include_games)
    if collection is None:
        raise AppException(404, 'RESOURCE_NOT_FOUND', f'Collection with id {collection_id} was not found.')
    return collection


def ensure_collection_owner(collection: Collection, user: User) -> None:
    if collection.user_id != user.id:
        raise AppException(403, 'FORBIDDEN', 'You do not have permission to modify this collection.')


def ensure_collection_visible(collection: Collection, user: User | None) -> None:
    if collection.is_public:
        return
    if user is None or user.id != collection.user_id:
        raise AppException(403, 'FORBIDDEN', 'You do not have permission to view this private collection.')