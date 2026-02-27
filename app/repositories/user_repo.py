from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)


def get_user_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.scalar(stmt)


def create_user(db: Session, *, email: str, hashed_password: str, display_name: str | None) -> User:
    user = User(email=email, hashed_password=hashed_password, display_name=display_name)
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, *, display_name: str | None = None, hashed_password: str | None = None) -> User:
    if display_name is not None:
        user.display_name = display_name
    if hashed_password is not None:
        user.hashed_password = hashed_password
    db.add(user)
    db.flush()
    db.refresh(user)
    return user