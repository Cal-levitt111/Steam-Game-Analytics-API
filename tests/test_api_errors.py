from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from tests.auth_helpers import create_auth_tables, issue_auth_headers


@pytest.fixture()
def authenticated_client() -> tuple[TestClient, dict[str, str]]:
    engine = create_engine(
        'sqlite+pysqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    create_auth_tables(engine)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client, issue_auth_headers(client, email='errors@example.com')
    app.dependency_overrides.clear()


def test_search_missing_q_returns_400_with_standard_envelope(
    authenticated_client: tuple[TestClient, dict[str, str]]
) -> None:
    client, headers = authenticated_client
    response = client.get('/api/v1/search', headers=headers)
    assert response.status_code == 400
    body = response.json()
    assert body['error']['code'] == 'BAD_REQUEST'


def test_auth_me_without_token_returns_401_with_bearer_header() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/auth/me')
    assert response.status_code == 401
    assert response.json()['error']['code'] == 'UNAUTHORIZED'
    assert response.headers.get('WWW-Authenticate') == 'Bearer'


def test_validation_error_uses_standard_envelope() -> None:
    client = TestClient(app)
    response = client.post('/api/v1/auth/register', json={'email': 'bad', 'password': '123'})
    assert response.status_code == 422
    body = response.json()
    assert body['error']['code'] == 'VALIDATION_ERROR'
    assert isinstance(body['error']['detail'], list)


def test_catalog_requires_token() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/games')
    assert response.status_code == 401
    assert response.json()['error']['code'] == 'UNAUTHORIZED'
    assert response.headers.get('WWW-Authenticate') == 'Bearer'


def test_not_found_uses_standard_envelope() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/does-not-exist')
    assert response.status_code == 404
    assert response.json()['error']['code'] == 'RESOURCE_NOT_FOUND'


def test_jwks_requires_token() -> None:
    client = TestClient(app)
    response = client.get('/.well-known/jwks.json')
    assert response.status_code == 401
    assert response.json()['error']['code'] == 'UNAUTHORIZED'
