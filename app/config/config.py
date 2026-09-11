import os
from enum import Enum

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Valid application environments."""

    DEVELOPMENT = "dev"  # default
    TEST = "test"
    UAT = "uat"
    PRODUCTION = "prod"


_environment = os.getenv("APP_ENV", "dev")


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: SecretStr | None = None
    ANTHROPIC_MODEL: str | None = "claude-haiku-4-5-20251001"

    model_config = SettingsConfigDict(
        env_file=f".env.{_environment}",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
