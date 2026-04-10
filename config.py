# config.py 
'''
Configuration component (DesignSpec: Configuration)
Loads DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, and JWT_EXPIRE_MINUTES
from .env file using pydantic
'''

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    '''All application settings sourced form environment variables'''

    DATABASE_URL: str = ""
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Module level singleton - import `settings` everywhere instead of
# re-instantiating Settings() in each module.
settings = Settings()