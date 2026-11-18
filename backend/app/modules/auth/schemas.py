"""Pydantic schemas for authentication requests and responses."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """User credentials for authentication."""

    email: EmailStr = Field(description="User account email")
    password: str = Field(min_length=1, description="Plaintext account password")


class RefreshTokenRequest(BaseModel):
    """Payload to exchange a refresh token for a new token pair."""

    refresh_token: str = Field(min_length=1, description="Opaque refresh token")


class LogoutRequest(BaseModel):
    """Optional payload when logging out to specify which refresh token family to revoke."""

    refresh_token: Optional[str] = Field(default=None, description="Optional refresh token string to revoke")


class TokenResponse(BaseModel):
    """Access and refresh token response matching docs/API_CONTRACT.md."""

    access_token: str = Field(description="Short-lived JWT access token")
    refresh_token: str = Field(description="Opaque rotating refresh token")
    token_type: str = Field(default="bearer", description="Token scheme type")
    expires_in: int = Field(description="Access token lifespan in seconds")
