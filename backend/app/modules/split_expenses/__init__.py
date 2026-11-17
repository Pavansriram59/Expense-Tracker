"""Split Expenses module package."""

from app.modules.split_expenses.router import router
from app.modules.split_expenses.service import SplitExpenseService

__all__ = ["router", "SplitExpenseService"]
