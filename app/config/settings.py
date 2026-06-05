"""Application configuration using Pydantic Settings."""

import os
from typing import Literal

from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings

_env = os.getenv("APP_ENV", "development")


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    model_config = ConfigDict(
        env_file=(".env", f".env.{_env}"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    app_env: Literal["development", "test", "uat", "production"] = "development"
    debug: bool = False

    @model_validator(mode="after")
    def validate_secrets(self) -> "Settings":
        if self.app_env == "production":
            if not self.secret_key or self.secret_key == "dev-secret-change-in-production":
                raise ValueError("SECRET_KEY must be set in production")
            if not self.jwt_secret or self.jwt_secret == "dev-secret-change-in-production":
                raise ValueError("JWT_SECRET must be set in production")
        return self

    # Database
    database_url: str = "postgresql://vibedrive:vibedrive@localhost:5432/vibedrive"
    database_pool_size: int = 10
    database_pool_timeout: int = 30

    # Flask
    secret_key: str = "dev-secret-change-in-production"
    json_sort_keys: bool = False

    # Auth
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "learning_resources"

    # OpenAI / LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo"

    # App
    app_name: str = "VibeDrive"
    app_version: str = "0.1.0"


settings = Settings()
