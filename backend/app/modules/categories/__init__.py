"""Categories module package."""

from app.modules.categories.router import router
from app.modules.categories.service import CategoryService

__all__ = ["router", "CategoryService"]
