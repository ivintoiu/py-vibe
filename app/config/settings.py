"""Application configuration using Pydantic Settings."""

from typing import Literal

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    environment: Literal["development", "test", "uat", "production"] = "development"
    debug: bool = False

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
