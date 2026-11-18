"""Authentication domain service managing credentials, JWTs, and refresh token families."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_token,
    verify_password,
)
from app.modules.auth.models import RefreshToken
from app.modules.auth.schemas import TokenResponse
from app.modules.users.models import User
from app.modules.users.schemas import UserRegisterRequest
from app.modules.users.service import UserService

settings = get_settings()


class AuthService:
    """Domain service managing user registration, authentication, and token lifecycle."""

    def __init__(self, user_service: Optional[UserService] = None) -> None:
        self.user_service = user_service or UserService()

    async def register(self, db: AsyncSession, schema: UserRegisterRequest) -> User:
        """Register a new user account."""
        return await self.user_service.create_user(db, schema)

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> TokenResponse:
        """Authenticate user credentials and issue an initial access and refresh token pair."""
        normalized_email = email.strip().lower()
        user = await self.user_service.get_by_email(db, normalized_email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException(
                detail="Invalid email or password.",
                code="INVALID_CREDENTIALS",
            )

        if not user.is_active:
            raise ForbiddenException(
                detail="Your account has been deactivated. Please contact support.",
                code="USER_DEACTIVATED",
            )

        # 1. Create short-lived JWT access token
        access_token = create_access_token(
            subject=str(user.id),
            email=user.email,
        )

        # 2. Create rotating refresh token family
        raw_refresh_token, token_hash = generate_refresh_token()
        family_id = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
            revoked=False,
        )
        db.add(refresh_record)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_tokens(self, db: AsyncSession, refresh_token_str: str) -> TokenResponse:
        """Rotate a refresh token: invalidate current token, check reuse, and issue new pair."""
        token_hash = hash_token(refresh_token_str.strip())

        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        record = result.scalar_one_or_none()

        if not record:
            raise UnauthorizedException(
                detail="Invalid or unrecognized refresh token.",
                code="INVALID_REFRESH_TOKEN",
            )

        # Token Reuse Detection: if this token was already revoked, invalidate entire family!
        if record.revoked:
            await db.execute(
                update(RefreshToken)
                .where(RefreshToken.family_id == record.family_id)
                .values(revoked=True)
            )
            await db.commit()
            raise UnauthorizedException(
                detail="Refresh token reuse detected. All sessions in this family have been invalidated for security.",
                code="TOKEN_REUSE_DETECTED",
            )

        # Expiration Check (ensuring timezone awareness across both PostgreSQL and SQLite)
        now = datetime.now(timezone.utc)
        expires_at = record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            record.revoked = True
            await db.commit()
            raise UnauthorizedException(
                detail="Refresh token has expired. Please log in again.",
                code="REFRESH_TOKEN_EXPIRED",
            )

        # Mark current refresh token as consumed/revoked
        record.revoked = True

        # Fetch associated user
        user = await self.user_service.get_by_id(db, record.user_id)
        if not user or not user.is_active:
            await db.commit()
            raise UnauthorizedException(
                detail="User account is inactive or no longer exists.",
                code="USER_INACTIVE",
            )

        # Issue new token pair retaining the same family_id
        access_token = create_access_token(
            subject=str(user.id),
            email=user.email,
        )
        new_raw_token, new_token_hash = generate_refresh_token()
        new_expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        new_record = RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            family_id=record.family_id,
            expires_at=new_expires_at,
            revoked=False,
        )
        db.add(new_record)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_raw_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def logout(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        refresh_token_str: Optional[str] = None,
    ) -> None:
        """Revoke active refresh tokens for the user."""
        if refresh_token_str:
            token_hash = hash_token(refresh_token_str.strip())
            result = await db.execute(
                select(RefreshToken).where(RefreshToken.token_hash == token_hash)
            )
            record = result.scalar_one_or_none()
            if record:
                # Invalidate the specific token family
                await db.execute(
                    update(RefreshToken)
                    .where(RefreshToken.family_id == record.family_id)
                    .values(revoked=True)
                )
                await db.commit()
                return

        # Fallback: Invalidate all active tokens for this user
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
            .values(revoked=True)
        )
        await db.commit()
