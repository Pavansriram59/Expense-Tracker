"""Pydantic schemas for user registration, responses, and profile updates."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """Payload for registering a new user."""

    email: EmailStr = Field(description="Unique email address for authentication")
    password: str = Field(min_length=8, max_length=128, description="Secure account password (min 8 chars)")
    full_name: str = Field(min_length=1, max_length=150, description="User full display name")
    base_currency: str = Field(default="INR", min_length=3, max_length=3, description="ISO-4217 Currency Code (default: INR)")

    @field_validator("base_currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        code = v.strip().upper()
        if len(code) != 3 or not code.isalpha():
            raise ValueError("base_currency must be a 3-letter ISO-4217 currency code (e.g., INR, USD, EUR)")
        return code

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        name = v.strip()
        if not name:
            raise ValueError("full_name cannot be blank")
        return name


class UserUpdateRequest(BaseModel):
    """Payload for updating user profile fields."""

    full_name: Optional[str] = Field(default=None, min_length=1, max_length=150, description="Updated display name")
    base_currency: Optional[str] = Field(default=None, min_length=3, max_length=3, description="Updated ISO-4217 Currency Code")

    @field_validator("base_currency")
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        code = v.strip().upper()
        if len(code) != 3 or not code.isalpha():
            raise ValueError("base_currency must be a 3-letter ISO-4217 currency code")
        return code

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        name = v.strip()
        if not name:
            raise ValueError("full_name cannot be blank")
        return name


class UserResponse(BaseModel):
    """Public user profile response representation."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    base_currency: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
