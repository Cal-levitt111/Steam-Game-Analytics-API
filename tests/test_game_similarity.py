import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.exceptions import AppException
from app.main import app
from app.routers import games as games_router_module
from tests.auth_helpers import create_auth_tables, issue_auth_headers


@pytest.fixture()
def similarity_client() -> tuple[TestClient, dict[str, str]]:
    engine = create_engine('sqlite+pysqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    create_auth_tables(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE games (
                    id INTEGER PRIMARY KEY,
                    steam_app_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    embedding TEXT
                )
                """
            )
        )

    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client, issue_auth_headers(client, email='similarity@example.com')
    app.dependency_overrides.clear()


def test_similar_games_returns_501_when_vector_not_supported(
    similarity_client: tuple[TestClient, dict[str, str]]
) -> None:
    client, headers = similarity_client
    response = client.get('/api/v1/games/1/similar', headers=headers)
    assert response.status_code == 501
    assert response.json()['error']['code'] == 'FEATURE_UNAVAILABLE'


def test_similar_games_404_passthrough(
    similarity_client: tuple[TestClient, dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, headers = similarity_client

    def fake_list_similar_games(*args, **kwargs):
        raise AppException(404, 'RESOURCE_NOT_FOUND', 'missing')

    monkeypatch.setattr(games_router_module, 'list_similar_games', fake_list_similar_games)
    response = client.get('/api/v1/games/999/similar', headers=headers)
    assert response.status_code == 404
    assert response.json()['error']['code'] == 'RESOURCE_NOT_FOUND'


def test_similar_games_409_passthrough(
    similarity_client: tuple[TestClient, dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, headers = similarity_client

    def fake_list_similar_games(*args, **kwargs):
        raise AppException(409, 'EMBEDDING_NOT_AVAILABLE', 'no embedding')

    monkeypatch.setattr(games_router_module, 'list_similar_games', fake_list_similar_games)
    response = client.get('/api/v1/games/1/similar', headers=headers)
    assert response.status_code == 409
    assert response.json()['error']['code'] == 'EMBEDDING_NOT_AVAILABLE'


def test_similar_games_success_shape(
    similarity_client: tuple[TestClient, dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, headers = similarity_client
    monkeypatch.setattr(games_router_module, 'list_similar_games', lambda *args, **kwargs: ([], {}))
    response = client.get('/api/v1/games/1/similar?limit=5', headers=headers)
    assert response.status_code == 200
    assert response.json() == {'data': []}


def test_similar_games_limit_validation(similarity_client: tuple[TestClient, dict[str, str]]) -> None:
    client, headers = similarity_client
    response = client.get('/api/v1/games/1/similar?limit=0', headers=headers)
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'VALIDATION_ERROR'
