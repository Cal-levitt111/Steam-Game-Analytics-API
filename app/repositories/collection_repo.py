from sqlalchemy import Select, func, insert, select
from sqlalchemy.orm import Session, selectinload

from app.models.collection import Collection, collection_games
from app.models.game import Game


def create_collection(
    db: Session,
    *,
    user_id: int,
    name: str,
    description: str | None,
    is_public: bool,
) -> Collection:
    collection = Collection(user_id=user_id, name=name, description=description, is_public=is_public)
    db.add(collection)
    db.flush()
    db.refresh(collection)
    return collection


def get_collection_by_id(db: Session, collection_id: int, include_games: bool = False) -> Collection | None:
    stmt: Select = select(Collection).where(Collection.id == collection_id)
    if include_games:
        stmt = stmt.options(selectinload(Collection.games))
    return db.scalar(stmt)


def list_user_collections(db: Session, *, user_id: int, page: int, per_page: int) -> tuple[list[tuple[Collection, int]], int]:
    stmt: Select = (
        select(Collection, func.count(collection_games.c.game_id).label('game_count'))
        .outerjoin(collection_games, collection_games.c.collection_id == Collection.id)
        .where(Collection.user_id == user_id)
        .group_by(Collection.id)
        .order_by(Collection.created_at.desc(), Collection.id.desc())
    )
    total = db.scalar(select(func.count()).select_from(Collection).where(Collection.user_id == user_id)) or 0
    offset = (page - 1) * per_page
    rows = list(db.execute(stmt.offset(offset).limit(per_page)).all())
    return rows, total


def list_public_collections(db: Session, *, page: int, per_page: int, order: str) -> tuple[list[tuple[Collection, int]], int]:
    count_expr = func.count(collection_games.c.game_id).label('game_count')
    stmt: Select = (
        select(Collection, count_expr)
        .outerjoin(collection_games, collection_games.c.collection_id == Collection.id)
        .where(Collection.is_public.is_(True))
        .group_by(Collection.id)
    )
    if order == 'game_count':
        stmt = stmt.order_by(count_expr.desc(), Collection.created_at.desc())
    else:
        stmt = stmt.order_by(Collection.created_at.desc(), Collection.id.desc())

    total = db.scalar(select(func.count()).select_from(Collection).where(Collection.is_public.is_(True))) or 0
    offset = (page - 1) * per_page
    rows = list(db.execute(stmt.offset(offset).limit(per_page)).all())
    return rows, total


def update_collection(
    db: Session,
    collection: Collection,
    *,
    name: str | None,
    description: str | None,
    is_public: bool | None,
) -> Collection:
    if name is not None:
        collection.name = name
    if description is not None:
        collection.description = description
    if is_public is not None:
        collection.is_public = is_public
    db.add(collection)
    db.flush()
    db.refresh(collection)
    return collection


def delete_collection(db: Session, collection: Collection) -> None:
    db.delete(collection)


def game_exists(db: Session, game_id: int) -> bool:
    return db.scalar(select(func.count()).select_from(Game).where(Game.id == game_id)) > 0


def collection_has_game(db: Session, collection_id: int, game_id: int) -> bool:
    stmt = (
        select(func.count())
        .select_from(collection_games)
        .where(collection_games.c.collection_id == collection_id, collection_games.c.game_id == game_id)
    )
    return db.scalar(stmt) > 0


def add_game_to_collection(db: Session, collection_id: int, game_id: int) -> None:
    db.execute(insert(collection_games).values(collection_id=collection_id, game_id=game_id))


def remove_game_from_collection(db: Session, collection_id: int, game_id: int) -> int:
    stmt = collection_games.delete().where(
        collection_games.c.collection_id == collection_id,
        collection_games.c.game_id == game_id,
    )
    result = db.execute(stmt)
    return result.rowcount or 0