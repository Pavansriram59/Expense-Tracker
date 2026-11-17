"""Health check endpoints for application status and database connectivity."""

import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Application Health Check",
    response_description="Current service health status and metadata",
)
async def health_check() -> Dict[str, Any]:
    """Basic liveness probe checking if the API service is running."""
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get(
    "/health/db",
    status_code=status.HTTP_200_OK,
    summary="Database Connectivity Check",
    response_description="Database readiness status and round-trip query latency",
)
async def database_health_check(
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Readiness probe checking database connectivity by executing a lightweight query."""
    start_time = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ok",
                "database": "connected",
                "latency_ms": round(latency_ms, 2),
            },
        )
    except Exception as exc:
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "latency_ms": round(latency_ms, 2),
                "error": str(exc),
            },
        )
