"""Users module package."""

from app.modules.users.router import router
from app.modules.users.service import UserService

__all__ = ["router", "UserService"]
