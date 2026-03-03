from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Steam Games Analytics API'
    app_version: str = '0.1.0'
    api_prefix: str = '/api/v1'

    environment: str = Field(default='development', alias='ENVIRONMENT')
    database_url: str = Field(default='postgresql+psycopg://steam:steam@localhost:5432/steamgames', alias='DATABASE_URL')
    secret_key: str = Field(default='change-me-in-production', alias='SECRET_KEY')
    access_token_expire_minutes: int = Field(default=1440, alias='ACCESS_TOKEN_EXPIRE_MINUTES')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
