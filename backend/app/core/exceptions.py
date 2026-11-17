"""Global domain exceptions and RFC 7807-compliant HTTP exception handlers."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


# =============================================================================
# Domain Exceptions (Raised in Services / Core, Never directly returning HTTP)
# =============================================================================

HTTP_422_STATUS = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", status.HTTP_422_UNPROCESSABLE_ENTITY)


class AppException(Exception):
    """Base exception for all application domain errors."""

    def __init__(
        self,
        detail: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.code = code
        self.status_code = status_code
        self.errors = errors or []


class NotFoundException(AppException):
    """Resource not found error."""

    def __init__(
        self,
        detail: str = "Requested resource was not found",
        code: str = "RESOURCE_NOT_FOUND",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_404_NOT_FOUND,
            errors=errors,
        )


class ConflictException(AppException):
    """Resource conflict error (e.g. duplicate key or state collision)."""

    def __init__(
        self,
        detail: str = "Resource conflict detected",
        code: str = "RESOURCE_CONFLICT",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_409_CONFLICT,
            errors=errors,
        )


class ValidationException(AppException):
    """Business rule validation failure."""

    def __init__(
        self,
        detail: str = "Validation failed",
        code: str = "VALIDATION_ERROR",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            detail=detail,
            code=code,
            status_code=HTTP_422_STATUS,
            errors=errors,
        )


class UnauthorizedException(AppException):
    """Authentication required or token invalid."""

    def __init__(
        self,
        detail: str = "Authentication required",
        code: str = "UNAUTHORIZED",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=errors,
        )


class ForbiddenException(AppException):
    """Insufficient privileges."""

    def __init__(
        self,
        detail: str = "Access forbidden",
        code: str = "FORBIDDEN",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_403_FORBIDDEN,
            errors=errors,
        )


class DatabaseConnectionException(AppException):
    """Database connectivity failure."""

    def __init__(
        self,
        detail: str = "Database connection unavailable",
        code: str = "DATABASE_UNAVAILABLE",
    ) -> None:
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# =============================================================================
# Response Builder
# =============================================================================

def build_error_response(
    status_code: int,
    code: str,
    detail: str,
    request: Request,
    errors: Optional[List[Dict[str, Any]]] = None,
) -> JSONResponse:
    """Standardized error envelope matching docs/API_CONTRACT.md."""
    request_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID", "-")
    content: Dict[str, Any] = {
        "code": code,
        "detail": detail,
        "errors": errors or [],
        "request_id": request_id,
    }
    return JSONResponse(status_code=status_code, content=content)


# =============================================================================
# FastAPI Global Exception Handlers
# =============================================================================

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application domain exceptions."""
    logger.warning("Domain exception occurred [%s]: %s", exc.code, exc.detail)
    return build_error_response(
        status_code=exc.status_code,
        code=exc.code,
        detail=exc.detail,
        request=request,
        errors=exc.errors,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic and FastAPI request validation errors."""
    formatted_errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        formatted_errors.append({
            "field": field or "body",
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        })

    logger.info("Request validation failed: %d errors", len(formatted_errors))
    return build_error_response(
        status_code=HTTP_422_STATUS,
        code="VALIDATION_ERROR",
        detail="Request input validation failed.",
        request=request,
        errors=formatted_errors,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard Starlette / FastAPI HTTPExceptions."""
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "RESOURCE_NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    return build_error_response(
        status_code=exc.status_code,
        code=code,
        detail=str(exc.detail),
        request=request,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled exceptions (500). Prevents internal leaks."""
    logger.exception("Unhandled server exception: %s", str(exc))
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        detail="An unexpected internal server error occurred.",
        request=request,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application."""
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
