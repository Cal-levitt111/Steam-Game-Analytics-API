from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.auth_rate_limit import AuthRateLimitCounter


def get_counter_for_update(db: Session, *, scope: str, identifier_hash: str) -> AuthRateLimitCounter | None:
    stmt = (
        select(AuthRateLimitCounter)
        .where(
            AuthRateLimitCounter.scope == scope,
            AuthRateLimitCounter.identifier_hash == identifier_hash,
        )
        .with_for_update()
    )
    return db.scalar(stmt)


def create_counter(
    db: Session,
    *,
    scope: str,
    identifier_hash: str,
    now: datetime,
) -> AuthRateLimitCounter:
    counter = AuthRateLimitCounter(
        scope=scope,
        identifier_hash=identifier_hash,
        window_started_at=now,
        attempt_count=0,
        blocked_until=None,
        updated_at=now,
    )
    db.add(counter)
    db.flush()
    return counter


def save_counter(db: Session, counter: AuthRateLimitCounter, *, now: datetime) -> None:
    counter.updated_at = now
    db.add(counter)
    db.flush()


def delete_counter(db: Session, *, scope: str, identifier_hash: str) -> None:
    db.execute(
        delete(AuthRateLimitCounter).where(
            AuthRateLimitCounter.scope == scope,
            AuthRateLimitCounter.identifier_hash == identifier_hash,
        )
    )
