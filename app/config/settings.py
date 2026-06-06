"""Application configuration using Pydantic Settings."""

import os
from functools import lru_cache

from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_env = os.getenv("APP_ENV", "dev")


class VibeDriveSettings(BaseSettings):
    """Application configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{_env}"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -- App ------------------------------------------------------------------
    app_name: str = "VibeDrive"
    app_version: str = "0.1.0"
    debug: bool = False

    # -- Database -------------------------------------------------------------

    database_url: SecretStr | None = None

    @field_validator("database_url", mode="after")
    @classmethod
    def validate_database_url(cls, v: SecretStr | None) -> SecretStr:
        if v is None:
            raise ValueError("DATABASE_URL is required but not set!")
        PostgresDsn(v.get_secret_value())
        return v

    database_pool_size: int = 10
    database_pool_timeout: int = 30

    # -- Auth -----------------------------------------------------------------
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # Redis
    redis_url: str = "redis://localhost:6379/0"


@lru_cache(maxsize=1)
def get_settings() -> VibeDriveSettings:
    return VibeDriveSettings()
