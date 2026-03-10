from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine

from app.models.auth_rate_limit import AuthRateLimitCounter
from app.models.user import User


def create_auth_tables(engine: Engine) -> None:
    User.__table__.create(bind=engine, checkfirst=True)
    AuthRateLimitCounter.__table__.create(bind=engine, checkfirst=True)


def issue_auth_headers(
    client: TestClient,
    *,
    email: str,
    password: str = 'StrongPass123',
    display_name: str | None = None,
) -> dict[str, str]:
    client.post(
        '/api/v1/auth/register',
        json={
            'email': email,
            'password': password,
            'display_name': display_name or email,
        },
    )
    login = client.post('/api/v1/auth/login', json={'email': email, 'password': password})
    token = login.json()['access_token']
    return {'Authorization': f'Bearer {token}'}
