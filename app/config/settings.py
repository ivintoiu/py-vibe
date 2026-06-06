"""Application configuration using Pydantic Settings."""

import os
from functools import lru_cache

from pydantic import PostgresDsn, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_env = os.getenv("APP_ENV", "development")

_PLACEHOLDER = "dev-secret-change-in-production"
_PROD_ENVS = {"production", "prod"}


class VibeDriveSettings(BaseSettings):
    """Application configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{_env}"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -- App ------------------------------------------------------------------
    app_env: str = "development"
    app_name: str = "VibeDrive"
    app_version: str = "0.1.0"
    debug: bool = False

    # -- Database -------------------------------------------------------------

    database_url: SecretStr | None = None

    @field_validator("database_url", mode="after")
    @classmethod
    def validate_database_url(cls, v: SecretStr | None) -> SecretStr | None:
        if v is not None and v.get_secret_value():
            PostgresDsn(v.get_secret_value())
        return v

    database_pool_size: int = 10
    database_pool_timeout: int = 30

    # -- Flask ----------------------------------------------------------------
    secret_key: str = _PLACEHOLDER

    # -- Auth -----------------------------------------------------------------
    jwt_secret: str = _PLACEHOLDER
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "VibeDriveSettings":
        if self.app_env in _PROD_ENVS:
            if not self.database_url or not self.database_url.get_secret_value():
                raise ValueError("DATABASE_URL must be set in production")
            if self.secret_key == _PLACEHOLDER:
                raise ValueError("SECRET_KEY must be set in production")
            if self.jwt_secret == _PLACEHOLDER:
                raise ValueError("JWT_SECRET must be set in production")
        return self


@lru_cache(maxsize=1)
def get_settings() -> VibeDriveSettings:
    return VibeDriveSettings()
