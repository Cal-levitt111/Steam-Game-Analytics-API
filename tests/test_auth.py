import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models.auth_rate_limit import AuthRateLimitCounter
from app.models.user import User


@pytest.fixture()
def client() -> TestClient:
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


def test_register_and_login_success(client: TestClient) -> None:
    register_payload = {
        'email': 'user@example.com',
        'password': 'StrongPass123',
        'display_name': 'User One',
    }

    register_response = client.post('/api/v1/auth/register', json=register_payload)
    assert register_response.status_code == 201
    assert register_response.json()['email'] == 'user@example.com'
    assert 'Location' in register_response.headers

    login_response = client.post(
        '/api/v1/auth/login',
        json={'email': 'user@example.com', 'password': 'StrongPass123'},
    )
    assert login_response.status_code == 200
    body = login_response.json()
    assert body['token_type'] == 'bearer'
    assert body['access_token']


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    payload = {'email': 'dupe@example.com', 'password': 'StrongPass123', 'display_name': 'Dupe'}
    assert client.post('/api/v1/auth/register', json=payload).status_code == 201

    duplicate_response = client.post('/api/v1/auth/register', json=payload)
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()['error']['code'] == 'EMAIL_TAKEN'


def test_auth_me_requires_token_and_supports_profile_update(client: TestClient) -> None:
    client.post(
        '/api/v1/auth/register',
        json={'email': 'me@example.com', 'password': 'StrongPass123', 'display_name': 'Before'},
    )

    unauthenticated = client.get('/api/v1/auth/me')
    assert unauthenticated.status_code == 401

    login_response = client.post('/api/v1/auth/login', json={'email': 'me@example.com', 'password': 'StrongPass123'})
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    me_response = client.get('/api/v1/auth/me', headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()['display_name'] == 'Before'

    update_response = client.put('/api/v1/auth/me', headers=headers, json={'display_name': 'After'})
    assert update_response.status_code == 200
    assert update_response.json()['display_name'] == 'After'


def test_login_bad_password_returns_401(client: TestClient) -> None:
    client.post(
        '/api/v1/auth/register',
        json={'email': 'badpass@example.com', 'password': 'StrongPass123', 'display_name': 'User'},
    )

    login_response = client.post('/api/v1/auth/login', json={'email': 'badpass@example.com', 'password': 'Wrong'})
    assert login_response.status_code == 401
    assert login_response.json()['error']['code'] == 'INVALID_CREDENTIALS'
