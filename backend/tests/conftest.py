"""Pytest fixtures for backend testing."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    """Override application settings for test environment."""
    return Settings(
        PROJECT_NAME="Personal Finance Tracker (Test)",
        ENVIRONMENT="test",
        DEBUG=True,
        SECRET_KEY="test-secret-key-not-for-production",
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
    )


@pytest_asyncio.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create in-memory SQLite async engine per test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated database session per test function."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(test_engine: AsyncEngine, test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client with database dependency override."""
    app = create_app()

    # Override get_settings
    app.dependency_overrides[get_settings] = lambda: test_settings

    # Override get_db to use test engine
    test_session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
