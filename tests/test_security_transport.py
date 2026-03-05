from fastapi.testclient import TestClient

from app import main as main_module


def _build_client(
    monkeypatch,
    *,
    force_https: bool,
    allowed_hosts: list[str],
    trusted_proxy_cidrs: list[str],
    hsts_max_age_seconds: int = 63072000,
) -> TestClient:
    monkeypatch.setattr(main_module.settings, 'force_https', force_https)
    monkeypatch.setattr(main_module.settings, 'allowed_hosts', allowed_hosts)
    monkeypatch.setattr(main_module.settings, 'trusted_proxy_cidrs', trusted_proxy_cidrs)
    monkeypatch.setattr(main_module.settings, 'hsts_max_age_seconds', hsts_max_age_seconds)
    app = main_module.create_app()
    return TestClient(
        app,
        base_url='http://127.0.0.1:8000',
        follow_redirects=False,
        client=('127.0.0.1', 50000),
    )


def test_force_https_redirects_http_requests(monkeypatch) -> None:
    client = _build_client(
        monkeypatch,
        force_https=True,
        allowed_hosts=['127.0.0.1'],
        trusted_proxy_cidrs=[],
    )
    response = client.get('/api/v1/health')

    assert response.status_code == 307
    assert response.headers['location'] == 'https://127.0.0.1:8000/api/v1/health'


def test_trusted_proxy_forwarded_https_skips_redirect_and_sets_hsts(monkeypatch) -> None:
    client = _build_client(
        monkeypatch,
        force_https=True,
        allowed_hosts=['127.0.0.1'],
        trusted_proxy_cidrs=['127.0.0.1/32'],
    )
    response = client.get('/api/v1/health', headers={'X-Forwarded-Proto': 'https'})

    assert response.status_code == 200
    assert response.headers['strict-transport-security'].startswith('max-age=63072000')
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert response.headers['x-frame-options'] == 'DENY'


def test_untrusted_proxy_forwarded_https_is_ignored(monkeypatch) -> None:
    client = _build_client(
        monkeypatch,
        force_https=True,
        allowed_hosts=['127.0.0.1'],
        trusted_proxy_cidrs=['10.0.0.0/8'],
    )
    response = client.get('/api/v1/health', headers={'X-Forwarded-Proto': 'https'})

    assert response.status_code == 307
    assert response.headers['location'] == 'https://127.0.0.1:8000/api/v1/health'


def test_disallowed_host_returns_400(monkeypatch) -> None:
    monkeypatch.setattr(main_module.settings, 'force_https', False)
    monkeypatch.setattr(main_module.settings, 'allowed_hosts', ['api.example.com'])
    monkeypatch.setattr(main_module.settings, 'trusted_proxy_cidrs', [])
    monkeypatch.setattr(main_module.settings, 'hsts_max_age_seconds', 63072000)
    app = main_module.create_app()

    client = TestClient(
        app,
        base_url='http://127.0.0.1:8000',
        follow_redirects=False,
        client=('127.0.0.1', 50000),
    )
    response = client.get('/api/v1/health')
    assert response.status_code == 400
