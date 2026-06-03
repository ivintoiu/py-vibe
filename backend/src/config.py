from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://vibedrive:vibedrive@localhost:5432/vibedrive"
    database_pool_size: int = 10
    database_pool_timeout: int = 30

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
    openai_model: str = "gpt-4-turbo-preview"

    # App
    app_name: str = "VibeDrive"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
