import base64
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import os
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings

ALGORITHM = 'HS256'
PBKDF2_ITERATIONS = 390000


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode('utf-8')


def _b64_decode(raw: str) -> bytes:
    return base64.urlsafe_b64decode(raw.encode('utf-8'))


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ITERATIONS)
    return f'pbkdf2_sha256${PBKDF2_ITERATIONS}${_b64_encode(salt)}${_b64_encode(derived_key)}'


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations, salt_b64, hash_b64 = hashed_password.split('$', 3)
        if algorithm != 'pbkdf2_sha256':
            return False
        salt = _b64_decode(salt_b64)
        expected = _b64_decode(hash_b64)
        candidate = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, int(iterations))
        return hmac.compare_digest(candidate, expected)
    except Exception:
        return False


def create_access_token(subject: str, expires_delta_minutes: int | None = None) -> str:
    now = datetime.now(UTC)
    expire_minutes = expires_delta_minutes or settings.access_token_expire_minutes
    payload: dict[str, Any] = {
        'sub': subject,
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=expire_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except ExpiredSignatureError as exc:
        raise ValueError('TOKEN_EXPIRED') from exc
    except JWTError as exc:
        raise ValueError('TOKEN_INVALID') from exc