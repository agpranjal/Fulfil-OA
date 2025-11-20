"""Application configuration using environment variables."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Product Importer"
    database_url: str = "postgresql+psycopg2://app:app@db:5432/product_importer"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    temp_upload_dir: str = "./tmp/uploads"
    webhook_timeout_seconds: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
