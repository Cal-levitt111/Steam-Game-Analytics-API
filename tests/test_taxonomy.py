import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models.game import Developer, Genre, Publisher, Tag, game_developers, game_genres, game_publishers, game_tags


@pytest.fixture()
def taxonomy_client() -> TestClient:
    engine = create_engine('sqlite+pysqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)

    with engine.begin() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE games (
                id INTEGER PRIMARY KEY,
                steam_app_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                short_description TEXT,
                detailed_description TEXT,
                release_date DATE,
                price_usd NUMERIC,
                is_free BOOLEAN DEFAULT 0,
                metacritic_score SMALLINT,
                positive_reviews INTEGER DEFAULT 0,
                negative_reviews INTEGER DEFAULT 0,
                required_age SMALLINT DEFAULT 0,
                website TEXT,
                header_image TEXT,
                windows BOOLEAN DEFAULT 0,
                mac BOOLEAN DEFAULT 0,
                linux BOOLEAN DEFAULT 0,
                search_vector TEXT,
                created_at TEXT
            )
            """
        )

    Tag.__table__.create(bind=engine)
    Developer.__table__.create(bind=engine)
    Publisher.__table__.create(bind=engine)
    Genre.__table__.create(bind=engine)
    game_tags.create(bind=engine)
    game_developers.create(bind=engine)
    game_publishers.create(bind=engine)
    game_genres.create(bind=engine)

    with engine.begin() as conn:
        conn.execute(text("INSERT INTO tags (id, name, slug) VALUES (1, 'Indie', 'indie'), (2, 'Action', 'action')"))
        conn.execute(text("INSERT INTO developers (id, name, slug) VALUES (1, 'Valve', 'valve'), (2, 'Indie Forge', 'indie-forge')"))
        conn.execute(text("INSERT INTO publishers (id, name, slug) VALUES (1, 'EA', 'ea'), (2, 'Valve', 'valve-pub')"))
        conn.execute(text("INSERT INTO genres (id, name, slug) VALUES (1, 'RPG', 'rpg'), (2, 'Strategy', 'strategy')"))

        conn.execute(text("INSERT INTO game_tags (game_id, tag_id) VALUES (1, 1), (2, 1), (3, 2)"))
        conn.execute(text("INSERT INTO game_developers (game_id, developer_id) VALUES (1, 1), (2, 1), (3, 2)"))
        conn.execute(text("INSERT INTO game_publishers (game_id, publisher_id) VALUES (1, 1), (2, 1), (3, 2)"))
        conn.execute(text("INSERT INTO game_genres (game_id, genre_id) VALUES (1, 1), (2, 1), (3, 2)"))

    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_tags_list_and_detail_counts(taxonomy_client: TestClient) -> None:
    list_response = taxonomy_client.get('/api/v1/tags')
    assert list_response.status_code == 200
    body = list_response.json()
    assert body['data'][0]['slug'] == 'indie'
    assert body['data'][0]['game_count'] == 2

    detail_response = taxonomy_client.get('/api/v1/tags/indie')
    assert detail_response.status_code == 200
    assert detail_response.json()['data']['game_count'] == 2


def test_slug_not_found_responses(taxonomy_client: TestClient) -> None:
    publisher_response = taxonomy_client.get('/api/v1/publishers/missing')
    assert publisher_response.status_code == 404
    assert publisher_response.json()['error']['code'] == 'RESOURCE_NOT_FOUND'

    genre_games_response = taxonomy_client.get('/api/v1/genres/missing/games')
    assert genre_games_response.status_code == 404
    assert genre_games_response.json()['error']['code'] == 'RESOURCE_NOT_FOUND'


def test_developer_and_publisher_counts(taxonomy_client: TestClient) -> None:
    dev_response = taxonomy_client.get('/api/v1/developers?q=val')
    assert dev_response.status_code == 200
    assert len(dev_response.json()['data']) == 1
    assert dev_response.json()['data'][0]['slug'] == 'valve'
    assert dev_response.json()['data'][0]['game_count'] == 2

    pub_response = taxonomy_client.get('/api/v1/publishers')
    assert pub_response.status_code == 200
    assert pub_response.json()['data'][0]['game_count'] == 2