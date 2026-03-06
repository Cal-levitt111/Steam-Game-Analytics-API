from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppException
from app.repositories.auth_rate_limit_repo import create_counter, delete_counter, get_counter_for_update, save_counter

LOGIN_EMAIL_SCOPE = 'login_email'
LOGIN_IP_SCOPE = 'login_ip'
REGISTER_IP_SCOPE = 'register_ip'
UNKNOWN_IP = 'unknown'


def normalize_client_ip(client_host: str | None) -> str:
    return client_host.strip() if client_host else UNKNOWN_IP


def enforce_login_rate_limit(db: Session, *, email: str, client_ip: str) -> None:
    if not settings.auth_rate_limit_enabled:
        return
    _assert_scope_not_blocked(db, scope=LOGIN_EMAIL_SCOPE, identifier=email.lower().strip())
    _assert_scope_not_blocked(db, scope=LOGIN_IP_SCOPE, identifier=client_ip)


def record_login_failure(db: Session, *, email: str, client_ip: str) -> None:
    if not settings.auth_rate_limit_enabled:
        return
    retry_after_values = [
        _record_attempt(
            db,
            scope=LOGIN_EMAIL_SCOPE,
            identifier=email.lower().strip(),
            max_attempts=settings.auth_rate_limit_login_email_max_attempts,
        ),
        _record_attempt(
            db,
            scope=LOGIN_IP_SCOPE,
            identifier=client_ip,
            max_attempts=settings.auth_rate_limit_login_ip_max_attempts,
        ),
    ]
    retry_after_seconds = max((value or 0) for value in retry_after_values)
    if retry_after_seconds > 0:
        raise _too_many_attempts_exception(retry_after_seconds)


def clear_login_failures(db: Session, *, email: str, client_ip: str) -> None:
    if not settings.auth_rate_limit_enabled:
        return
    delete_counter(db, scope=LOGIN_EMAIL_SCOPE, identifier_hash=_hash_identifier(LOGIN_EMAIL_SCOPE, email.lower().strip()))
    delete_counter(db, scope=LOGIN_IP_SCOPE, identifier_hash=_hash_identifier(LOGIN_IP_SCOPE, client_ip))
    db.commit()


def consume_register_ip_attempt(db: Session, *, client_ip: str) -> None:
    if not settings.auth_rate_limit_enabled:
        return
    retry_after_seconds = _record_attempt(
        db,
        scope=REGISTER_IP_SCOPE,
        identifier=client_ip,
        max_attempts=settings.auth_rate_limit_register_ip_max_attempts,
    )
    if retry_after_seconds:
        raise _too_many_attempts_exception(retry_after_seconds)


def _assert_scope_not_blocked(db: Session, *, scope: str, identifier: str) -> None:
    now = datetime.now(UTC)
    counter = get_counter_for_update(db, scope=scope, identifier_hash=_hash_identifier(scope, identifier))
    if counter is None:
        return

    blocked_until = _as_utc(counter.blocked_until) if counter.blocked_until else None
    window_started_at = _as_utc(counter.window_started_at)

    changed = False
    if blocked_until and blocked_until <= now:
        _reset_counter_window(counter, now)
        changed = True
    elif now - window_started_at >= timedelta(seconds=settings.auth_rate_limit_window_seconds):
        _reset_counter_window(counter, now)
        changed = True

    if changed:
        save_counter(db, counter, now=now)
        db.commit()
        blocked_until = _as_utc(counter.blocked_until) if counter.blocked_until else None

    if blocked_until and blocked_until > now:
        retry_after_seconds = max(1, int((blocked_until - now).total_seconds()))
        raise _too_many_attempts_exception(retry_after_seconds)


def _record_attempt(db: Session, *, scope: str, identifier: str, max_attempts: int) -> int | None:
    now = datetime.now(UTC)
    counter = get_counter_for_update(db, scope=scope, identifier_hash=_hash_identifier(scope, identifier))
    if counter is None:
        counter = create_counter(
            db,
            scope=scope,
            identifier_hash=_hash_identifier(scope, identifier),
            now=now,
        )

    blocked_until = _as_utc(counter.blocked_until) if counter.blocked_until else None
    window_started_at = _as_utc(counter.window_started_at)

    if blocked_until and blocked_until > now:
        retry_after_seconds = max(1, int((blocked_until - now).total_seconds()))
        return retry_after_seconds

    if blocked_until and blocked_until <= now:
        _reset_counter_window(counter, now)
    elif now - window_started_at >= timedelta(seconds=settings.auth_rate_limit_window_seconds):
        _reset_counter_window(counter, now)

    counter.attempt_count += 1

    retry_after_seconds: int | None = None
    if counter.attempt_count > max_attempts:
        blocked_until = now + timedelta(seconds=settings.auth_rate_limit_block_seconds)
        counter.blocked_until = blocked_until
        retry_after_seconds = settings.auth_rate_limit_block_seconds

    save_counter(db, counter, now=now)
    db.commit()
    return retry_after_seconds


def _hash_identifier(scope: str, identifier: str) -> str:
    value = f'{scope}:{identifier}'.encode('utf-8')
    return hashlib.sha256(value).hexdigest()


def _reset_counter_window(counter, now: datetime) -> None:
    counter.window_started_at = now
    counter.attempt_count = 0
    counter.blocked_until = None


def _too_many_attempts_exception(retry_after_seconds: int) -> AppException:
    return AppException(
        429,
        'TOO_MANY_REQUESTS',
        'Too many authentication attempts. Please retry later.',
        headers={'Retry-After': str(retry_after_seconds)},
    )


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
