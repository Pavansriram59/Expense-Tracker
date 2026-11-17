"""Centralized application settings driven by environment variables."""

import json
from functools import lru_cache
from typing import Any, List, Union

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    PROJECT_NAME: str = "Personal Finance Tracker"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="development | staging | production | test")
    DEBUG: bool = Field(default=False, description="Debug mode flag")

    # Security
    SECRET_KEY: str = Field(
        default="insecure-dev-secret-key-change-this-in-production-use-openssl-rand-hex-32",
        description="Secret key for JWT generation",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="Access token lifetime in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token lifetime in days")

    # PostgreSQL Database
    POSTGRES_SERVER: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    POSTGRES_USER: str = Field(default="postgres", description="PostgreSQL user")
    POSTGRES_PASSWORD: str = Field(default="postgres_password", description="PostgreSQL password")
    POSTGRES_DB: str = Field(default="financetracker", description="PostgreSQL database name")
    DATABASE_URL: str | None = Field(
        default=None,
        description="Async database connection string. If omitted, built from POSTGRES_* settings.",
    )

    # Database Pool Settings
    DB_POOL_SIZE: int = Field(default=5, description="Queue pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Pool connection timeout in seconds")

    # CORS Allowed Origins
    CORS_ORIGINS: Union[List[str], str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:4200",
            "http://localhost:8000",
        ],
        description="Allowed CORS origin domains (list or comma-separated string)",
    )

    # Structured Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    LOG_FORMAT: str = Field(default="json", description="Log output format: json | text")

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        """Convert comma-separated string or json string into a list of strings."""
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        return []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def async_database_url(self) -> str:
        """Return the async database URL, generating from parts if not explicitly provided."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_database_url(self) -> str:
        """Return a sync driver URL (for Alembic or tools requiring sync drivers)."""
        url = self.async_database_url
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "")
        if "+aiosqlite" in url:
            return url.replace("+aiosqlite", "")
        return url


def parse_cors_origins(v: Any) -> List[str]:
    """Helper function to parse origins for tests or standalone usage."""
    return Settings.assemble_cors_origins(v)


@lru_cache
def get_settings() -> Settings:
    """Cached singleton instance of application settings."""
    return Settings()
