from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repo


def register_user(db: Session, *, email: str, password: str, display_name: str | None) -> User:
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


def login_user(db: Session, *, email: str, password: str) -> tuple[User, str]:
    user = user_repo.get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise AppException(401, 'INVALID_CREDENTIALS', 'Email or password is incorrect.')

    token = create_access_token(str(user.id))
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