"""Anthropic LLM configuration."""

import os
from enum import Enum
from functools import lru_cache

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_environment = os.getenv("APP_ENV", "dev")
_PROD_ENVS = {"production", "prod"}
_PLACEHOLDER = "dev-secret-change-in-production"


class Environment(str, Enum):
    """Valid application environments."""

    DEVELOPMENT = "dev"  # default
    TEST = "test"
    UAT = "uat"
    PRODUCTION = "prod"


class AnthropicSettings(BaseSettings):
    """Configuration for Anthropic LLM integration."""

    app_env: str = os.getenv("APP_ENV", "dev")
    anthropic_api_key: SecretStr | None = None
    anthropic_model: str = "claude-haiku-4-5-20251001"

    model_config = SettingsConfigDict(
        env_file=f".env.{_environment}",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "AnthropicSettings":
        """Ensure API key is configured in production."""
        if self.app_env in _PROD_ENVS and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in production")
        return self


@lru_cache(maxsize=1)
def get_settings() -> AnthropicSettings:
    """Get cached Anthropic settings instance."""
    return AnthropicSettings()


settings = get_settings()
