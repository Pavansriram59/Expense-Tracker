"""Accounts module package."""

from app.modules.accounts.router import router
from app.modules.accounts.service import AccountService

__all__ = ["router", "AccountService"]
