from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
