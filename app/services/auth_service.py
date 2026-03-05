from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repo
from app.services.auth_rate_limit_service import (
    clear_login_failures,
    consume_register_ip_attempt,
    enforce_login_rate_limit,
    normalize_client_ip,
    record_login_failure,
)


def register_user(db: Session, *, email: str, password: str, display_name: str | None, client_ip: str | None) -> User:
    consume_register_ip_attempt(db, client_ip=normalize_client_ip(client_ip))
    existing = user_repo.get_user_by_email(db, email)
    if existing:
        raise AppException(409, 'EMAIL_TAKEN', 'A user with that email already exists.')

    user = user_repo.create_user(
        db,
        email=email,
        hashed_password=hash_password(password),
        display_name=display_name,
    )
    db.commit()
    return user


def login_user(db: Session, *, email: str, password: str, client_ip: str | None) -> tuple[User, str]:
    normalized_ip = normalize_client_ip(client_ip)
    enforce_login_rate_limit(db, email=email, client_ip=normalized_ip)

    user = user_repo.get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        record_login_failure(db, email=email, client_ip=normalized_ip)
        raise AppException(401, 'INVALID_CREDENTIALS', 'Email or password is incorrect.')

    token = create_access_token(str(user.id))
    clear_login_failures(db, email=email, client_ip=normalized_ip)
    return user, token


def update_current_user(
    db: Session,
    user: User,
    *,
    display_name: str | None,
    new_password: str | None,
) -> User:
    hashed_password = hash_password(new_password) if new_password else None
    updated = user_repo.update_user(db, user, display_name=display_name, hashed_password=hashed_password)
    db.commit()
    return updated
