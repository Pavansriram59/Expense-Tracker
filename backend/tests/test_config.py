"""Tests verifying centralized Pydantic settings and env parsing."""

from app.core.config import Settings, parse_cors_origins


def test_settings_defaults() -> None:
    """Verify default settings values when initialized without overrides."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/testdb"
    )
    assert settings.PROJECT_NAME == "Personal Finance Tracker"
    assert settings.VERSION == "1.0.0"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
    assert settings.DB_POOL_SIZE == 5
    assert "postgresql+asyncpg" in settings.async_database_url
    assert "+asyncpg" not in settings.sync_database_url


def test_cors_origins_parsing() -> None:
    """Verify comma-separated origins and list origins are parsed correctly."""
    # Comma-separated string
    parsed_str = parse_cors_origins("http://localhost:3000, https://myapp.com , ")
    assert parsed_str == ["http://localhost:3000", "https://myapp.com"]

    # List of strings
    parsed_list = parse_cors_origins(["http://localhost:4200", "http://localhost:8000"])
    assert parsed_list == ["http://localhost:4200", "http://localhost:8000"]

    # None / Empty
    assert parse_cors_origins(None) == []


def test_computed_database_urls() -> None:
    """Verify URL generation from parts when DATABASE_URL is not provided."""
    settings = Settings(
        POSTGRES_SERVER="db.internal",
        POSTGRES_PORT=5433,
        POSTGRES_USER="db_user",
        POSTGRES_PASSWORD="secure_password",
        POSTGRES_DB="finance_prod",
        DATABASE_URL=None,
    )
    assert settings.async_database_url == (
        "postgresql+asyncpg://db_user:secure_password@db.internal:5433/finance_prod"
    )
    assert settings.sync_database_url == (
        "postgresql://db_user:secure_password@db.internal:5433/finance_prod"
    )
