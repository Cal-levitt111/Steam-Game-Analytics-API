import base64
from datetime import UTC, datetime, timedelta
from functools import lru_cache
import hashlib
import hmac
import os
from typing import Any
from uuid import uuid4

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings

JWT_ALGORITHM = 'RS256'
LEGACY_HS256_ALGORITHM = 'HS256'
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
        'nbf': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=expire_minutes)).timestamp()),
        'iss': settings.jwt_issuer,
        'aud': settings.jwt_audience,
        'jti': str(uuid4()),
    }
    headers = {'kid': settings.jwt_active_kid}
    return jwt.encode(payload, _get_active_private_key(), algorithm=JWT_ALGORITHM, headers=headers)


def decode_access_token(token: str) -> dict[str, Any]:
    now = datetime.now(UTC)
    try:
        header = jwt.get_unverified_header(token)
        algorithm = header.get('alg')
        if algorithm == LEGACY_HS256_ALGORITHM:
            if _legacy_hs256_is_allowed(now):
                return jwt.decode(
                    token,
                    settings.secret_key,
                    algorithms=[LEGACY_HS256_ALGORITHM],
                    options={
                        'verify_iss': False,
                        'verify_aud': False,
                        'leeway': settings.jwt_clock_skew_seconds,
                    },
                )
            raise ValueError('TOKEN_INVALID')
        if algorithm != JWT_ALGORITHM:
            raise ValueError('TOKEN_INVALID')
        kid = header.get('kid')
        if not isinstance(kid, str) or not kid:
            raise ValueError('TOKEN_INVALID')

        public_keys = get_public_key_ring()
        public_key = public_keys.get(kid)
        if public_key is None:
            raise ValueError('TOKEN_INVALID')

        return jwt.decode(
            token,
            public_key,
            algorithms=[JWT_ALGORITHM],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={'leeway': settings.jwt_clock_skew_seconds},
        )
    except ExpiredSignatureError as exc:
        raise ValueError('TOKEN_EXPIRED') from exc
    except JWTError as exc:
        raise ValueError('TOKEN_INVALID') from exc


def _legacy_hs256_is_allowed(now: datetime) -> bool:
    cutoff = settings.jwt_accept_legacy_hs256_until
    if cutoff is None:
        return False
    return now <= _as_utc(cutoff)


def get_public_key_ring() -> dict[str, str]:
    ring: dict[str, str] = {}
    for kid, key in settings.jwt_additional_public_keys.items():
        if kid.strip() and isinstance(key, str) and key.strip():
            ring[kid.strip()] = key.strip()
    ring[settings.jwt_active_kid] = _get_active_public_key()
    return ring


def get_jwks_document() -> dict[str, list[dict[str, str]]]:
    keys = [_public_pem_to_jwk(kid, pem) for kid, pem in get_public_key_ring().items()]
    return {'keys': keys}


def _get_active_private_key() -> str:
    configured = settings.jwt_active_private_key.strip()
    if configured:
        return configured
    return _get_development_private_key()


def _get_active_public_key() -> str:
    configured = settings.jwt_active_public_key.strip()
    if configured:
        return configured
    return _derive_public_key_pem(_get_active_private_key())


@lru_cache
def _get_development_private_key() -> str:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode('utf-8')


def _derive_public_key_pem(private_key_pem: str) -> str:
    private_key = load_pem_private_key(private_key_pem.encode('utf-8'), password=None)
    public_key = private_key.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode('utf-8')


def _public_pem_to_jwk(kid: str, public_key_pem: str) -> dict[str, str]:
    key = load_pem_public_key(public_key_pem.encode('utf-8'))
    if not isinstance(key, rsa.RSAPublicKey):
        raise ValueError('Only RSA public keys are supported for JWKS output.')
    numbers = key.public_numbers()
    return {
        'kty': 'RSA',
        'use': 'sig',
        'alg': JWT_ALGORITHM,
        'kid': kid,
        'n': _int_to_base64url(numbers.n),
        'e': _int_to_base64url(numbers.e),
    }


def _int_to_base64url(value: int) -> str:
    byte_length = max(1, (value.bit_length() + 7) // 8)
    raw = value.to_bytes(byte_length, byteorder='big')
    return base64.urlsafe_b64encode(raw).decode('utf-8').rstrip('=')


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
