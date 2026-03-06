from fastapi import APIRouter

from app.core.security import get_jwks_document

router = APIRouter(tags=['jwks'])


@router.get('/.well-known/jwks.json')
def get_jwks() -> dict[str, list[dict[str, str]]]:
    return get_jwks_document()
