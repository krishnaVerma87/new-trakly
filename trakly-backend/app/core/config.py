"""Application configuration using Pydantic Settings."""
import json
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Trakly"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "mysql+aiomysql://trakly_user:trakly_pass@localhost:3309/trakly"

    # JWT Authentication
    JWT_SECRET_KEY: str = "trakly-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3003", "http://localhost", "http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    # Email Settings (supports both SMTP_* and EMAIL_* env var names)
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 587
    EMAIL_HOST_USER: str = ""
    EMAIL_HOST_PASSWORD: str = ""
    EMAIL_USE_TLS: bool = True
    DEFAULT_FROM_EMAIL: str = "noreply@trakly.com"
    FROM_NAME: str = "Trakly"

    # Legacy aliases for backward compatibility
    @property
    def SMTP_HOST(self) -> str:
        return self.EMAIL_HOST

    @property
    def SMTP_PORT(self) -> int:
        return self.EMAIL_PORT

    @property
    def SMTP_USER(self) -> str:
        return self.EMAIL_HOST_USER

    @property
    def SMTP_PASSWORD(self) -> str:
        return self.EMAIL_HOST_PASSWORD

    @property
    def SMTP_USE_TLS(self) -> bool:
        return self.EMAIL_USE_TLS

    @property
    def FROM_EMAIL(self) -> str:
        return self.DEFAULT_FROM_EMAIL

    # Slack Settings (Optional)
    SLACK_WEBHOOK_URL: Optional[str] = None
    SLACK_ENABLED: bool = False

    # Scheduler Settings
    SCHEDULER_ENABLED: bool = True
    REMINDER_CHECK_INTERVAL_MINUTES: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
