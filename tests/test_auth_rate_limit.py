from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models.auth_rate_limit import AuthRateLimitCounter
from app.models.user import User


@pytest.fixture()
def rate_limited_client(monkeypatch) -> TestClient:
    monkeypatch.setattr('app.core.config.settings.auth_rate_limit_enabled', True)
    monkeypatch.setattr('app.core.config.settings.auth_rate_limit_window_seconds', 900)
    monkeypatch.setattr('app.core.config.settings.auth_rate_limit_block_seconds', 60)
    monkeypatch.setattr('app.core.config.settings.auth_rate_limit_login_email_max_attempts', 2)
    monkeypatch.setattr('app.core.config.settings.auth_rate_limit_login_ip_max_attempts', 10)
    monkeypatch.setattr('app.core.config.settings.auth_rate_limit_register_ip_max_attempts', 1)

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


def test_login_rate_limit_blocks_after_repeated_failures(rate_limited_client: TestClient) -> None:
    client = rate_limited_client
    client.post(
        '/api/v1/auth/register',
        json={'email': 'limited@example.com', 'password': 'StrongPass123', 'display_name': 'Limited'},
    )

    for _ in range(2):
        bad_response = client.post('/api/v1/auth/login', json={'email': 'limited@example.com', 'password': 'Wrong'})
        assert bad_response.status_code == 401
        assert bad_response.json()['error']['code'] == 'INVALID_CREDENTIALS'

    blocked_response = client.post('/api/v1/auth/login', json={'email': 'limited@example.com', 'password': 'Wrong'})
    assert blocked_response.status_code == 429
    assert blocked_response.json()['error']['code'] == 'TOO_MANY_REQUESTS'
    assert blocked_response.headers.get('Retry-After') == '60'


def test_register_rate_limit_blocks_by_ip(rate_limited_client: TestClient) -> None:
    client = rate_limited_client
    first = client.post(
        '/api/v1/auth/register',
        json={'email': 'one@example.com', 'password': 'StrongPass123', 'display_name': 'One'},
    )
    assert first.status_code == 201

    second = client.post(
        '/api/v1/auth/register',
        json={'email': 'two@example.com', 'password': 'StrongPass123', 'display_name': 'Two'},
    )
    assert second.status_code == 429
    assert second.json()['error']['code'] == 'TOO_MANY_REQUESTS'
    assert second.headers.get('Retry-After') == '60'


def test_successful_login_clears_failure_counters(rate_limited_client: TestClient) -> None:
    client = rate_limited_client
    client.post(
        '/api/v1/auth/register',
        json={'email': 'reset@example.com', 'password': 'StrongPass123', 'display_name': 'Reset'},
    )

    bad_response = client.post('/api/v1/auth/login', json={'email': 'reset@example.com', 'password': 'Wrong'})
    assert bad_response.status_code == 401

    good_response = client.post('/api/v1/auth/login', json={'email': 'reset@example.com', 'password': 'StrongPass123'})
    assert good_response.status_code == 200

    bad_again = client.post('/api/v1/auth/login', json={'email': 'reset@example.com', 'password': 'Wrong'})
    assert bad_again.status_code == 401
    assert bad_again.json()['error']['code'] == 'INVALID_CREDENTIALS'
