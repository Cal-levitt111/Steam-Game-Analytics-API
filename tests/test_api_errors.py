from fastapi.testclient import TestClient

from app.main import app


def test_search_missing_q_returns_400_with_standard_envelope() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/search')
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


def test_not_found_uses_standard_envelope() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/does-not-exist')
    assert response.status_code == 404
    assert response.json()['error']['code'] == 'RESOURCE_NOT_FOUND'