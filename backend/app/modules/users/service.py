"""User domain service managing profile queries and updates."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.security import hash_password
from app.modules.users.models import User
from app.modules.users.schemas import UserRegisterRequest, UserUpdateRequest


class UserService:
    """Domain service managing user identity, registration, and profile updates."""

    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a user entity by its primary UUID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Fetch a user entity by unique email address (case-insensitive)."""
        normalized_email = email.strip().lower()
        result = await db.execute(select(User).where(User.email == normalized_email))
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, schema: UserRegisterRequest) -> User:
        """Create and persist a new user after verifying email uniqueness."""
        normalized_email = schema.email.strip().lower()
        existing = await self.get_by_email(db, normalized_email)
        if existing:
            raise ConflictException(
                detail=f"An account with email '{normalized_email}' is already registered.",
                code="EMAIL_ALREADY_EXISTS",
            )

        hashed_pwd = hash_password(schema.password)
        new_user = User(
            email=normalized_email,
            hashed_password=hashed_pwd,
            full_name=schema.full_name,
            base_currency=schema.base_currency,
            is_active=True,
            is_verified=False,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    async def update_profile(
        self,
        db: AsyncSession,
        user: User,
        schema: UserUpdateRequest,
    ) -> User:
        """Apply partial updates to user profile fields."""
        if schema.full_name is not None:
            user.full_name = schema.full_name
        if schema.base_currency is not None:
            user.base_currency = schema.base_currency

        user.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)
        return user
