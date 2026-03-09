from app.core.config import Settings, settings, validate_runtime_settings
from app.main import create_app


def test_validate_runtime_settings_rejects_insecure_production_config(monkeypatch) -> None:
    monkeypatch.setattr(settings, 'environment', 'production')
    monkeypatch.setattr(settings, 'force_https', False)
    monkeypatch.setattr(settings, 'allowed_hosts', [])
    monkeypatch.setattr(settings, 'secret_key', 'change-me-in-production')
    monkeypatch.setattr(settings, 'jwt_active_private_key', '')
    monkeypatch.setattr(settings, 'jwt_active_public_key', '')

    try:
        create_app()
        raise AssertionError('Expected production config validation to fail.')
    except RuntimeError as exc:
        message = str(exc)
        assert 'FORCE_HTTPS' in message
        assert 'ALLOWED_HOSTS' in message
        assert 'SECRET_KEY' in message
        assert 'JWT_ACTIVE_PRIVATE_KEY' in message
        assert 'JWT_ACTIVE_PUBLIC_KEY' in message


def test_validate_runtime_settings_allows_secure_production_config(monkeypatch) -> None:
    monkeypatch.setattr(settings, 'environment', 'production')
    monkeypatch.setattr(settings, 'force_https', True)
    monkeypatch.setattr(settings, 'allowed_hosts', ['api.example.com'])
    monkeypatch.setattr(settings, 'secret_key', 'real-production-secret')
    monkeypatch.setattr(settings, 'jwt_active_private_key', '-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----')
    monkeypatch.setattr(settings, 'jwt_active_public_key', '-----BEGIN PUBLIC KEY-----\nabc\n-----END PUBLIC KEY-----')

    app = create_app()
    assert app.title == settings.app_name


def test_settings_normalize_escaped_newlines_for_pem_values() -> None:
    configured = Settings(
        JWT_ACTIVE_PRIVATE_KEY='line1\\nline2',
        JWT_ACTIVE_PUBLIC_KEY='line3\\nline4',
        JWT_ADDITIONAL_PUBLIC_KEYS={'old': 'line5\\nline6'},
    )

    assert configured.jwt_active_private_key == 'line1\nline2'
    assert configured.jwt_active_public_key == 'line3\nline4'
    assert configured.jwt_additional_public_keys['old'] == 'line5\nline6'


def test_validate_runtime_settings_is_noop_outside_production(monkeypatch) -> None:
    monkeypatch.setattr(settings, 'environment', 'development')
    monkeypatch.setattr(settings, 'force_https', False)
    monkeypatch.setattr(settings, 'allowed_hosts', [])
    monkeypatch.setattr(settings, 'secret_key', 'change-me-in-production')
    monkeypatch.setattr(settings, 'jwt_active_private_key', '')
    monkeypatch.setattr(settings, 'jwt_active_public_key', '')

    validate_runtime_settings(settings)
