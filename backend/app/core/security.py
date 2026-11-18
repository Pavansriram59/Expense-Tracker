"""Security utilities: password hashing, JWT operations, and token hashing."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException

settings = get_settings()

ALGORITHM = "HS256"


# =============================================================================
# Password Hashing (bcrypt)
# =============================================================================

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with automatic salt generation."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# =============================================================================
# JWT Access Tokens
# =============================================================================

def create_access_token(
    subject: str,
    email: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate a signed JWT access token for a user."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": subject,
        "email": email,
        "type": "access",
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": secrets.token_hex(16),
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token.

    Raises UnauthorizedException if token is expired, invalid, or wrong type.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type", code="INVALID_TOKEN_TYPE")
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedException("Access token has expired", code="TOKEN_EXPIRED") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedException("Invalid access token", code="INVALID_TOKEN") from exc


# =============================================================================
# Refresh Tokens (Opaque + SHA-256 hash storage)
# =============================================================================

def hash_token(raw_token: str) -> str:
    """Compute SHA-256 hex digest of a token string for safe storage and lookup."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_refresh_token() -> Tuple[str, str]:
    """Generate a cryptographically secure opaque refresh token.

    Returns:
        (raw_token, token_hash)
    """
    raw_token = secrets.token_urlsafe(48)
    token_hash = hash_token(raw_token)
    return raw_token, token_hash
