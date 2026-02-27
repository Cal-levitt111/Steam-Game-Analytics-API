from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.repositories.taxonomy_repo import get_developer_by_slug, get_publisher_by_slug, get_tag_by_slug


def get_tag_or_404(db: Session, slug: str):
    tag = get_tag_by_slug(db, slug)
    if tag is None:
        raise AppException(404, 'RESOURCE_NOT_FOUND', f'Tag with slug {slug} was not found.')
    return tag


def get_developer_or_404(db: Session, slug: str):
    developer = get_developer_by_slug(db, slug)
    if developer is None:
        raise AppException(404, 'RESOURCE_NOT_FOUND', f'Developer with slug {slug} was not found.')
    return developer


def get_publisher_or_404(db: Session, slug: str):
    publisher = get_publisher_by_slug(db, slug)
    if publisher is None:
        raise AppException(404, 'RESOURCE_NOT_FOUND', f'Publisher with slug {slug} was not found.')
    return publisher