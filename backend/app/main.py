"""Personal Finance Tracker — FastAPI Application Entry Point."""

import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.health import router as health_router
from app.core.logging import setup_logging
from app.db.session import close_db_engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and graceful shutdown."""
    # Startup actions
    setup_logging(log_level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    yield
    # Shutdown actions
    await close_db_engine()


def create_app() -> FastAPI:
    """Application factory initializing FastAPI with middleware, routers, and handlers."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Stateless Modular Monolith Backend for Personal Finance Tracker",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Request Tracing & Timing Middleware
    @app.middleware("http")
    async def request_tracing_middleware(
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time.perf_counter()
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)

        process_time_ms = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{process_time_ms:.2f}"
        return response

    # 3. Global Exception Handlers
    register_exception_handlers(app)

    # 4. Mount Health Router at Root
    app.include_router(health_router)

    # 5. Mount API v1 Routers
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
    app.include_router(api_v1_router, prefix="/v1")  # Direct v1 alias matching docs/API_CONTRACT.md

    # 6. Welcome Root Endpoint
    @app.get("/", tags=["Root"])
    async def root_welcome() -> dict[str, str]:
        return {
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()
