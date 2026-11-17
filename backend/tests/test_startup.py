"""Tests verifying application initialization and startup."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint_returns_welcome_payload(client: AsyncClient) -> None:
    """Verify GET / returns application metadata."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert "environment" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


@pytest.mark.asyncio
async def test_openapi_schema_generated_successfully(client: AsyncClient) -> None:
    """Verify OpenAPI specification is accessible and valid JSON."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["openapi"].startswith("3.")
    assert "paths" in data
    assert "/health" in data["paths"]
    assert "/health/db" in data["paths"]


@pytest.mark.asyncio
async def test_swagger_docs_endpoint(client: AsyncClient) -> None:
    """Verify Swagger UI HTML is accessible at /docs."""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()


@pytest.mark.asyncio
async def test_request_id_and_timing_headers_present(client: AsyncClient) -> None:
    """Verify custom middleware adds X-Request-ID and X-Response-Time-Ms."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert "x-response-time-ms" in response.headers
    # If client sends a custom request ID, it should be reflected
    custom_id = "test-custom-request-id-12345"
    response_with_custom = await client.get("/health", headers={"X-Request-ID": custom_id})
    assert response_with_custom.headers["x-request-id"] == custom_id
