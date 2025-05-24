"""Application configuration settings."""
from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    APP_NAME: str = "JamSplitter"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "jamsplitter"
    DATABASE_URI: Optional[PostgresDsn] = None
    
    # Redis settings
    REDIS_URI: Optional[RedisDsn] = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    @property
    def database_url(self) -> str:
        """Get the database URL."""
        if self.DATABASE_URI is not None:
            return str(self.DATABASE_URI)
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings: The application settings.
    """
    return Settings()

# Create a settings instance for direct import
settings = get_settings()
