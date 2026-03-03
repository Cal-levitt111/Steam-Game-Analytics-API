from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppException
from app.models.game import Game
from app.repositories import game_repo


def list_games(db: Session, **filters):
    return game_repo.list_games(db, **filters)


def get_game_or_404(db: Session, game_id: int) -> Game:
    game = game_repo.get_game_by_id(db, game_id)
    if game is None:
        raise AppException(404, 'RESOURCE_NOT_FOUND', f'Game with id {game_id} was not found.')
    return game


def list_similar_games(db: Session, *, game_id: int, limit: int) -> tuple[list[Game], dict[int, float]]:
    if not settings.enable_vector_similarity:
        raise AppException(
            501,
            'FEATURE_UNAVAILABLE',
            'Vector similarity is disabled by configuration.',
        )

    if not game_repo.is_vector_similarity_supported(db):
        raise AppException(
            501,
            'FEATURE_UNAVAILABLE',
            'Vector similarity is not available in the current environment.',
        )

    game_state = game_repo.get_game_embedding_state(db, game_id)
    if game_state is None:
        raise AppException(404, 'RESOURCE_NOT_FOUND', f'Game with id {game_id} was not found.')

    _, has_embedding = game_state
    if not has_embedding:
        raise AppException(
            409,
            'EMBEDDING_NOT_AVAILABLE',
            f'Game with id {game_id} does not have an embedding yet.',
        )

    return game_repo.find_similar_games(db, game_id=game_id, limit=limit)
