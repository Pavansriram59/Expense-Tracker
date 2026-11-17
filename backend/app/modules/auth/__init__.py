"""Authentication module package."""

from app.modules.auth.router import router
from app.modules.auth.service import AuthService

__all__ = ["router", "AuthService"]
