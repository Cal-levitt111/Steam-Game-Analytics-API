from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, get_optional_current_user
from app.core.database import get_db
from app.core.pagination import build_pagination
from app.models.user import User
from app.repositories.collection_repo import list_public_collections, list_user_collections, update_collection as update_collection_repo
from app.schemas.collection import CollectionCreateRequest, CollectionDetail, CollectionListItem, CollectionRead, CollectionUpdateRequest
from app.services.collection_service import (
    create_collection,
    ensure_collection_owner,
    ensure_collection_visible,
    get_collection_or_404,
)

router = APIRouter(prefix='/collections', tags=['collections'])


@router.post('', response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
def create_collection_route(
    payload: CollectionCreateRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionRead:
    collection = create_collection(
        db,
        user=current_user,
        name=payload.name,
        description=payload.description,
        is_public=payload.is_public,
    )
    response.headers['Location'] = f'/api/v1/collections/{collection.id}'
    return CollectionRead.model_validate(collection)


@router.get('')
def list_my_collections(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    rows, total = list_user_collections(db, user_id=current_user.id, page=page, per_page=per_page)
    data = [
        CollectionListItem.model_validate(collection).model_dump() | {'game_count': int(game_count)}
        for collection, game_count in rows
    ]
    pagination = build_pagination(
        page=page,
        per_page=per_page,
        total=total,
        base_path='/api/v1/collections',
        query_params={},
    )
    return {'data': data, 'pagination': pagination}


@router.get('/public')
def list_public_collections_route(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default='created_at', pattern='^(created_at|game_count)$'),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    rows, total = list_public_collections(db, page=page, per_page=per_page, order=sort)
    data = [
        CollectionListItem.model_validate(collection).model_dump() | {'game_count': int(game_count)}
        for collection, game_count in rows
    ]
    pagination = build_pagination(
        page=page,
        per_page=per_page,
        total=total,
        base_path='/api/v1/collections/public',
        query_params={'sort': sort},
    )
    return {'data': data, 'pagination': pagination}


@router.get('/{collection_id}', response_model=CollectionDetail)
def get_collection_detail(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> CollectionDetail:
    collection = get_collection_or_404(db, collection_id, include_games=True)
    ensure_collection_visible(collection, current_user)
    return CollectionDetail.model_validate(collection)


@router.put('/{collection_id}', response_model=CollectionRead)
def update_collection_route(
    collection_id: int,
    payload: CollectionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionRead:
    collection = get_collection_or_404(db, collection_id)
    ensure_collection_owner(collection, current_user)
    updated = update_collection_repo(
        db,
        collection,
        name=payload.name,
        description=payload.description,
        is_public=payload.is_public,
    )
    db.commit()
    return CollectionRead.model_validate(updated)


@router.delete('/{collection_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_collection_route(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    collection = get_collection_or_404(db, collection_id)
    ensure_collection_owner(collection, current_user)
    db.delete(collection)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)