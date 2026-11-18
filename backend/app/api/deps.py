"""Shared API dependencies: authentication guards and database sessions."""

import uuid
from typing import TYPE_CHECKING, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import get_db

if TYPE_CHECKING:
    from app.modules.users.models import User

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> "User":
    """Validate JWT access token and return current authenticated User entity."""
    if not token:
        raise UnauthorizedException(
            detail="Authentication credentials were not provided.",
            code="NOT_AUTHENTICATED",
        )

    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException(
            detail="Invalid token payload: missing user identifier.",
            code="INVALID_TOKEN_SUBJECT",
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError as exc:
        raise UnauthorizedException(
            detail="Invalid token subject format.",
            code="INVALID_TOKEN_FORMAT",
        ) from exc

    # Avoid top-level circular import with user module
    from app.modules.users.service import UserService

    user_service = UserService()
    user = await user_service.get_by_id(db, user_uuid)
    if not user:
        raise UnauthorizedException(
            detail="User account no longer exists.",
            code="USER_NOT_FOUND",
        )

    if not user.is_active:
        raise ForbiddenException(
            detail="User account has been deactivated.",
            code="USER_INACTIVE",
        )

    return user


async def get_current_active_user(
    current_user: "User" = Depends(get_current_user),
) -> "User":
    """Ensure current user is active."""
    return current_user
