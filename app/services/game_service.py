from sqlalchemy.orm import Session

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