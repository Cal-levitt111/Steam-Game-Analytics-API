import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app


@pytest.fixture()
def analytics_client() -> TestClient:
    engine = create_engine('sqlite+pysqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE games (
                    id INTEGER PRIMARY KEY,
                    steam_app_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    short_description TEXT,
                    detailed_description TEXT,
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
                    search_vector TEXT,
                    created_at TEXT
                )
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO games (id, steam_app_id, name, price_usd, is_free, metacritic_score, positive_reviews, negative_reviews, windows, mac, linux)
                VALUES
                    (1, 1001, 'Free Co-op', 0, 1, 80, 90, 10, 1, 1, 0),
                    (2, 1002, 'Paid FPS', 19.99, 0, 60, 20, 80, 1, 0, 0),
                    (3, 1003, 'Linux Sim', 14.99, 0, 70, 50, 50, 0, 0, 1),
                    (4, 1004, 'Cross Platform', 0, 1, 75, 0, 0, 1, 1, 1)
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
        yield client
    app.dependency_overrides.clear()


def test_free_vs_paid_and_platform_breakdown(analytics_client: TestClient) -> None:
    free_paid = analytics_client.get('/api/v1/analytics/free-vs-paid')
    assert free_paid.status_code == 200
    body = free_paid.json()
    assert 'generated_at' in body
    assert 'query_params' in body
    assert len(body['data']) == 2

    platform = analytics_client.get('/api/v1/analytics/platform-breakdown')
    assert platform.status_code == 200
    row = platform.json()['data'][0]
    assert row['total_games'] == 4
    assert row['windows'] == 3
    assert row['linux'] == 2


def test_review_sentiment_distribution_shape(analytics_client: TestClient) -> None:
    response = analytics_client.get('/api/v1/analytics/review-sentiment')
    assert response.status_code == 200
    data = response.json()['data']
    assert len(data) == 10
    total_count = sum(item['count'] for item in data)
    assert total_count == 3
    assert all('bucket' in item and 'pct' in item for item in data)
