"""Application configuration using Pydantic Settings."""

import os
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration from environment variables."""

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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls,
            init_settings,
            env_settings,
            dotenv_settings,
            file_settings,
        ):
            """Load .env files with environment-specific overrides."""
            # First try environment-specific .env file
            env = os.getenv("ENVIRONMENT", "development")
            env_file = f".env.{env}"

            # Use environment-specific .env if it exists, otherwise use .env
            if os.path.exists(env_file):
                dotenv_settings = cls(env_file=env_file)
            else:
                dotenv_settings = cls(env_file=".env")

            return (init_settings, dotenv_settings, env_settings)


settings = Settings()
