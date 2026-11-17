"""Budgets module package."""

from app.modules.budgets.router import router
from app.modules.budgets.service import BudgetService

__all__ = ["router", "BudgetService"]
