"""Master API v1 router consolidating all modular monolith domain endpoints."""

from fastapi import APIRouter

from app.modules.accounts import router as accounts_router
from app.modules.analytics import router as analytics_router
from app.modules.auth import router as auth_router
from app.modules.budgets import router as budgets_router
from app.modules.categories import router as categories_router
from app.modules.settlements import router as settlements_router
from app.modules.split_expenses import router as split_expenses_router
from app.modules.transactions import router as transactions_router
from app.modules.users import router as users_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_v1_router.include_router(users_router, prefix="/users", tags=["users"])
api_v1_router.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
api_v1_router.include_router(transactions_router, prefix="/transactions", tags=["transactions"])
api_v1_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_v1_router.include_router(split_expenses_router, prefix="/splits", tags=["split-expenses"])
api_v1_router.include_router(settlements_router, prefix="/settlements", tags=["settlements"])
api_v1_router.include_router(budgets_router, prefix="/budgets", tags=["budgets"])
api_v1_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
