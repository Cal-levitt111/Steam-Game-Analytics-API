import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models.collection import Collection, collection_games
from app.models.user import User


@pytest.fixture()
def collections_client() -> tuple[TestClient, sessionmaker[Session]]:
    engine = create_engine('sqlite+pysqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)

    User.__table__.create(bind=engine)
    Collection.__table__.create(bind=engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE games (
                    id INTEGER PRIMARY KEY,
                    steam_app_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    release_date DATE,
                    estimated_owners TEXT,
                    peak_ccu INTEGER,
                    price_usd NUMERIC,
                    discount_percent SMALLINT,
                    dlc_count INTEGER,
                    about_the_game TEXT,
                    is_free BOOLEAN DEFAULT 0,
                    supported_languages TEXT,
                    full_audio_languages TEXT,
                    reviews TEXT,
                    support_url TEXT,
                    support_email TEXT,
                    metacritic_score SMALLINT,
                    metacritic_url TEXT,
                    user_score INTEGER,
                    positive_reviews INTEGER DEFAULT 0,
                    negative_reviews INTEGER DEFAULT 0,
                    score_rank TEXT,
                    achievements INTEGER,
                    recommendations INTEGER,
                    notes TEXT,
                    average_playtime_forever INTEGER,
                    average_playtime_two_weeks INTEGER,
                    median_playtime_forever INTEGER,
                    median_playtime_two_weeks INTEGER,
                    required_age SMALLINT DEFAULT 0,
                    website TEXT,
                    header_image TEXT,
                    windows BOOLEAN DEFAULT 0,
                    mac BOOLEAN DEFAULT 0,
                    linux BOOLEAN DEFAULT 0,
                    screenshots TEXT,
                    movies TEXT,
                    embedding TEXT,
                    search_vector TEXT,
                    created_at TEXT
                )
                """
            )
        )
    collection_games.create(bind=engine)

    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client, testing_session_local
    app.dependency_overrides.clear()


def _auth_headers(client: TestClient, email: str, password: str = 'StrongPass123') -> dict[str, str]:
    client.post('/api/v1/auth/register', json={'email': email, 'password': password, 'display_name': email})
    login = client.post('/api/v1/auth/login', json={'email': email, 'password': password})
    token = login.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_collections_crud_and_ownership(collections_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = collections_client

    unauthorized = client.post('/api/v1/collections', json={'name': 'My List'})
    assert unauthorized.status_code == 401

    owner_headers = _auth_headers(client, 'owner@example.com')
    other_headers = _auth_headers(client, 'other@example.com')

    create_resp = client.post(
        '/api/v1/collections',
        json={'name': 'Owner List', 'description': 'test', 'is_public': False},
        headers=owner_headers,
    )
    assert create_resp.status_code == 201
    collection_id = create_resp.json()['id']

    forbidden_update = client.put(
        f'/api/v1/collections/{collection_id}',
        json={'name': 'Hacked'},
        headers=other_headers,
    )
    assert forbidden_update.status_code == 403

    forbidden_delete = client.delete(f'/api/v1/collections/{collection_id}', headers=other_headers)
    assert forbidden_delete.status_code == 403


def test_collection_membership_conflict_and_not_found(collections_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, session_factory = collections_client

    headers = _auth_headers(client, 'member@example.com')
    create_resp = client.post('/api/v1/collections', json={'name': 'Games'}, headers=headers)
    collection_id = create_resp.json()['id']

    missing_game_add = client.post(f'/api/v1/collections/{collection_id}/games/999', headers=headers)
    assert missing_game_add.status_code == 404

    with session_factory() as db:
        db.execute(text("INSERT INTO games (id, steam_app_id, name) VALUES (10, 500010, 'Fixture Game')"))
        db.commit()

    add_resp = client.post(f'/api/v1/collections/{collection_id}/games/10', headers=headers)
    assert add_resp.status_code == 201

    duplicate_add = client.post(f'/api/v1/collections/{collection_id}/games/10', headers=headers)
    assert duplicate_add.status_code == 409

    remove_resp = client.delete(f'/api/v1/collections/{collection_id}/games/10', headers=headers)
    assert remove_resp.status_code == 204

    missing_remove = client.delete(f'/api/v1/collections/{collection_id}/games/10', headers=headers)
    assert missing_remove.status_code == 404


def test_public_collection_listing(collections_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = collections_client

    headers = _auth_headers(client, 'public@example.com')
    client.post('/api/v1/collections', json={'name': 'Visible', 'is_public': True}, headers=headers)

    public_resp = client.get('/api/v1/collections/public')
    assert public_resp.status_code == 200
    assert any(item['name'] == 'Visible' for item in public_resp.json()['data'])
