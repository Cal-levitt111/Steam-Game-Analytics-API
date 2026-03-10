from datetime import datetime
from functools import lru_cache
from typing import Annotated

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Steam Games Analytics API'
    app_version: str = '0.1.0'
    api_prefix: str = '/api/v1'

    environment: str = Field(default='development', alias='ENVIRONMENT')
    database_url: str = Field(default='postgresql+psycopg://steam:steam@localhost:5432/steamgames', alias='DATABASE_URL')
    secret_key: str = Field(default='change-me-in-production', alias='SECRET_KEY')
    access_token_expire_minutes: int = Field(default=1440, alias='ACCESS_TOKEN_EXPIRE_MINUTES')
    enable_vector_similarity: bool = Field(default=True, alias='ENABLE_VECTOR_SIMILARITY')
    embedding_model: str = Field(default='sentence-transformers/all-MiniLM-L6-v2', alias='EMBEDDING_MODEL')
    embedding_dim: int = Field(default=384, alias='EMBEDDING_DIM')
    embedding_batch_size: int = Field(default=64, alias='EMBEDDING_BATCH_SIZE')
    force_https: bool = Field(default=False, alias='FORCE_HTTPS')
    allowed_hosts: Annotated[list[str], NoDecode] = Field(default_factory=list, alias='ALLOWED_HOSTS')
    trusted_proxy_cidrs: Annotated[list[str], NoDecode] = Field(default_factory=list, alias='TRUSTED_PROXY_CIDRS')
    hsts_max_age_seconds: int = Field(default=63072000, alias='HSTS_MAX_AGE_SECONDS')
    auth_rate_limit_enabled: bool = Field(default=True, alias='AUTH_RATE_LIMIT_ENABLED')
    auth_rate_limit_window_seconds: int = Field(default=900, alias='AUTH_RATE_LIMIT_WINDOW_SECONDS')
    auth_rate_limit_block_seconds: int = Field(default=900, alias='AUTH_RATE_LIMIT_BLOCK_SECONDS')
    auth_rate_limit_login_email_max_attempts: int = Field(default=5, alias='AUTH_RATE_LIMIT_LOGIN_EMAIL_MAX_ATTEMPTS')
    auth_rate_limit_login_ip_max_attempts: int = Field(default=20, alias='AUTH_RATE_LIMIT_LOGIN_IP_MAX_ATTEMPTS')
    auth_rate_limit_register_ip_max_attempts: int = Field(default=10, alias='AUTH_RATE_LIMIT_REGISTER_IP_MAX_ATTEMPTS')
    jwt_issuer: str = Field(default='steam-games-analytics-api', alias='JWT_ISSUER')
    jwt_audience: str = Field(default='steam-games-analytics-clients', alias='JWT_AUDIENCE')
    jwt_active_kid: str = Field(default='dev-rs256-1', alias='JWT_ACTIVE_KID')
    jwt_active_private_key: str = Field(default='', alias='JWT_ACTIVE_PRIVATE_KEY')
    jwt_active_public_key: str = Field(default='', alias='JWT_ACTIVE_PUBLIC_KEY')
    jwt_additional_public_keys: dict[str, str] = Field(default_factory=dict, alias='JWT_ADDITIONAL_PUBLIC_KEYS')
    jwt_clock_skew_seconds: int = Field(default=60, alias='JWT_CLOCK_SKEW_SECONDS')
    jwt_accept_legacy_hs256_until: datetime | None = Field(default=None, alias='JWT_ACCEPT_LEGACY_HS256_UNTIL')
    enable_mcp_server: bool = Field(default=True, alias='ENABLE_MCP_SERVER')
    mcp_mount_path: str = Field(default='/mcp', alias='MCP_MOUNT_PATH')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)

    @field_validator('allowed_hosts', 'trusted_proxy_cidrs', mode='before')
    @classmethod
    def _parse_csv_list(cls, value: object) -> object:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value

    @field_validator('jwt_active_private_key', 'jwt_active_public_key', mode='before')
    @classmethod
    def _normalize_pem_value(cls, value: object) -> object:
        if isinstance(value, str):
            return value.replace('\\n', '\n').strip()
        return value

    @field_validator('jwt_additional_public_keys', mode='after')
    @classmethod
    def _normalize_public_key_ring(cls, value: dict[str, str], _: ValidationInfo) -> dict[str, str]:
        return {kid.strip(): key.replace('\\n', '\n').strip() for kid, key in value.items() if kid.strip() and key.strip()}


def is_production_environment(current_settings: Settings) -> bool:
    return current_settings.environment.strip().lower() == 'production'


def is_development_environment(current_settings: Settings) -> bool:
    return current_settings.environment.strip().lower() == 'development'


def validate_runtime_settings(current_settings: Settings) -> None:
    if not is_production_environment(current_settings):
        return

    failures: list[str] = []
    if not current_settings.force_https:
        failures.append('FORCE_HTTPS must be true in production.')
    if not current_settings.allowed_hosts:
        failures.append('ALLOWED_HOSTS must be configured in production.')
    if current_settings.secret_key.strip() in {'', 'change-me-in-production'}:
        failures.append('SECRET_KEY must not use the development placeholder in production.')
    if not current_settings.jwt_active_private_key:
        failures.append('JWT_ACTIVE_PRIVATE_KEY must be configured in production.')
    if not current_settings.jwt_active_public_key:
        failures.append('JWT_ACTIVE_PUBLIC_KEY must be configured in production.')

    if failures:
        joined = ' '.join(failures)
        raise RuntimeError(f'Invalid production security configuration. {joined}')


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
