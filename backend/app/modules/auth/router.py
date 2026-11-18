"""Authentication module router exposing registration, login, refresh, and logout."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.modules.auth.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.modules.auth.service import AuthService
from app.modules.users.models import User
from app.modules.users.schemas import UserRegisterRequest, UserResponse

router = APIRouter()
auth_service = AuthService()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Register New User",
    response_description="Created user profile metadata",
)
async def register_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Register a new user account with email, password, and name."""
    return await auth_service.register(db, payload)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Authenticate & Login",
    response_description="Access token and rotating refresh token",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate with credentials to obtain a JWT access token and refresh token."""
    return await auth_service.authenticate(db, payload.email, payload.password)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Rotate Refresh Token",
    response_description="New access token and rotated refresh token",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Exchange an active refresh token for a new token pair with family rotation."""
    return await auth_service.refresh_tokens(db, payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout & Revoke Tokens",
    response_description="Session invalidated",
)
async def logout(
    payload: Optional[LogoutRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Revoke active refresh tokens for the authenticated user session."""
    refresh_token_str = payload.refresh_token if payload else None
    await auth_service.logout(db, current_user.id, refresh_token_str)


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Auth Module Status",
)
async def get_auth_status() -> Dict[str, Any]:
    """Status endpoint verifying auth module availability."""
    return {"module": "auth", "status": "active", "ready": True}
