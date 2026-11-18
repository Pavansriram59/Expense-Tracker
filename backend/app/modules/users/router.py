"""Users module router exposing profile retrieval and updates."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse, UserUpdateRequest
from app.modules.users.service import UserService

router = APIRouter()
user_service = UserService()


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Get Current User Profile",
    response_description="Authenticated user profile and preferences",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    """Retrieve profile and preferences of the authenticated user."""
    return current_user


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Update User Profile",
    response_description="Updated user profile",
)
async def update_user_profile(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Partially update current user's profile information (full_name, base_currency)."""
    return await user_service.update_profile(db, current_user, payload)


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Users Module Status",
)
async def get_users_status() -> Dict[str, Any]:
    """Status endpoint verifying users module availability."""
    return {"module": "users", "status": "active", "ready": True}
