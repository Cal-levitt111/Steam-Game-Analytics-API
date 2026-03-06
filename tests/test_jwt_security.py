from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from jose import jwt as jose_jwt
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import get_db
from app.core.security import JWT_ALGORITHM, create_access_token, decode_access_token
from app.main import app
from app.models.auth_rate_limit import AuthRateLimitCounter
from app.models.user import User


@pytest.fixture()
def jwt_client() -> TestClient:
    engine = create_engine(
        'sqlite+pysqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    User.__table__.create(bind=engine)
    AuthRateLimitCounter.__table__.create(bind=engine)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_login_token_uses_rs256_kid_and_claims(jwt_client: TestClient) -> None:
    jwt_client.post(
        '/api/v1/auth/register',
        json={'email': 'jwt@example.com', 'password': 'StrongPass123', 'display_name': 'JWT'},
    )
    login = jwt_client.post('/api/v1/auth/login', json={'email': 'jwt@example.com', 'password': 'StrongPass123'})
    token = login.json()['access_token']

    header = jose_jwt.get_unverified_header(token)
    assert header['alg'] == JWT_ALGORITHM
    assert header['kid'] == settings.jwt_active_kid

    payload = decode_access_token(token)
    assert payload['sub']
    assert payload['iss'] == settings.jwt_issuer
    assert payload['aud'] == settings.jwt_audience
    assert payload['jti']
    assert payload['nbf']


def test_jwks_endpoint_exposes_active_key(jwt_client: TestClient) -> None:
    response = jwt_client.get('/.well-known/jwks.json')
    assert response.status_code == 200
    body = response.json()
    keys = body['keys']
    assert isinstance(keys, list)
    assert keys
    active = next(item for item in keys if item['kid'] == settings.jwt_active_kid)
    assert active['kty'] == 'RSA'
    assert active['alg'] == JWT_ALGORITHM
    assert active['n']
    assert active['e']


def test_decode_rejects_unknown_kid(monkeypatch) -> None:
    token = create_access_token('123')
    monkeypatch.setattr(settings, 'jwt_active_kid', 'new-active-kid')
    monkeypatch.setattr(settings, 'jwt_additional_public_keys', {})

    with pytest.raises(ValueError, match='TOKEN_INVALID'):
        decode_access_token(token)


def test_legacy_hs256_token_allowed_until_cutoff(monkeypatch) -> None:
    now = datetime.now(UTC)
    payload = {
        'sub': '42',
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=5)).timestamp()),
    }
    token = jose_jwt.encode(payload, settings.secret_key, algorithm='HS256')

    monkeypatch.setattr(settings, 'jwt_accept_legacy_hs256_until', now + timedelta(minutes=5))
    decoded = decode_access_token(token)
    assert decoded['sub'] == '42'


def test_legacy_hs256_token_rejected_after_cutoff(monkeypatch) -> None:
    now = datetime.now(UTC)
    payload = {
        'sub': '42',
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=5)).timestamp()),
    }
    token = jose_jwt.encode(payload, settings.secret_key, algorithm='HS256')

    monkeypatch.setattr(settings, 'jwt_accept_legacy_hs256_until', now - timedelta(minutes=1))
    with pytest.raises(ValueError, match='TOKEN_INVALID'):
        decode_access_token(token)
