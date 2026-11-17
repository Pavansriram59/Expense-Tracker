"""Tests verifying health-check endpoints and database connectivity."""

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.main import create_app


@pytest.mark.asyncio
async def test_health_check_returns_ok(client: AsyncClient) -> None:
    """Verify /health returns 200 with service metadata."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_database_health_check_connected(client: AsyncClient) -> None:
    """Verify /health/db succeeds when database session is valid."""
    response = await client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert isinstance(data["latency_ms"], (int, float))
    assert data["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_database_health_check_handles_disconnect(test_settings: Settings) -> None:
    """Verify /health/db returns 503 Service Unavailable when DB is unreachable."""
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: test_settings

    class MockBrokenSession:
        async def execute(self, *args: Any, **kwargs: Any) -> Any:
            raise ConnectionError("Simulated database connection failure")

    async def broken_get_db() -> AsyncGenerator[Any, None]:
        yield MockBrokenSession()

    app.dependency_overrides[get_db] = broken_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health/db")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"
        assert "Simulated database connection failure" in data["error"]
