"""Tests verifying domain exceptions and global RFC 7807 error envelopes."""

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.core.exceptions import (
    AppException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.main import create_app


class SampleBody(BaseModel):
    name: str
    amount: float


@pytest.mark.asyncio
async def test_standard_404_envelope(client: AsyncClient) -> None:
    """Verify non-existent route returns standard error envelope."""
    response = await client.get("/non-existent-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "RESOURCE_NOT_FOUND"
    assert "detail" in data
    assert "request_id" in data
    assert isinstance(data["errors"], list)


@pytest.mark.asyncio
async def test_validation_error_envelope(test_settings: Settings) -> None:
    """Verify Pydantic validation failure returns standard 422 envelope."""
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: test_settings

    @app.post("/test-validation")
    async def sample_endpoint(payload: SampleBody) -> dict[str, str]:
        return {"status": "ok"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/test-validation", json={})
        assert response.status_code == 422
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert len(data["errors"]) > 0
        assert any(e["field"] in ("name", "amount") for e in data["errors"])


@pytest.mark.asyncio
async def test_domain_app_exception_envelope(test_settings: Settings) -> None:
    """Verify custom domain exception returns custom code and status."""
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: test_settings

    @app.get("/trigger-conflict")
    async def trigger_conflict() -> None:
        raise ConflictException("An account with this suffix already exists", code="ACCOUNT_CONFLICT")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/trigger-conflict")
        assert response.status_code == 409
        data = response.json()
        assert data["code"] == "ACCOUNT_CONFLICT"
        assert "already exists" in data["detail"]
        assert "request_id" in data
