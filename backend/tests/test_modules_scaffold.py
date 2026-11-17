"""Tests verifying all 9 modular monolith packages are scaffolded and mounted."""

import pytest
from httpx import AsyncClient

MODULES_TO_TEST = [
    ("auth", "/api/v1/auth/status"),
    ("users", "/api/v1/users/status"),
    ("accounts", "/api/v1/accounts/status"),
    ("transactions", "/api/v1/transactions/status"),
    ("categories", "/api/v1/categories/status"),
    ("split_expenses", "/api/v1/splits/status"),
    ("settlements", "/api/v1/settlements/status"),
    ("budgets", "/api/v1/budgets/status"),
    ("analytics", "/api/v1/analytics/status"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("module_name,endpoint", MODULES_TO_TEST)
async def test_module_router_is_mounted_and_reachable(
    client: AsyncClient,
    module_name: str,
    endpoint: str,
) -> None:
    """Verify each module status endpoint responds with 200 OK."""
    response = await client.get(endpoint)
    assert response.status_code == 200, f"Module {module_name} endpoint {endpoint} failed"
    data = response.json()
    assert data["module"] == module_name
    assert data["status"] == "scaffolded"
    assert data["ready"] is True


def test_services_can_be_instantiated() -> None:
    """Verify all domain services can be instantiated cleanly."""
    from app.modules.accounts import AccountService
    from app.modules.analytics import AnalyticsService
    from app.modules.auth import AuthService
    from app.modules.budgets import BudgetService
    from app.modules.categories import CategoryService
    from app.modules.settlements import SettlementService
    from app.modules.split_expenses import SplitExpenseService
    from app.modules.transactions import TransactionService
    from app.modules.users import UserService

    services = [
        AuthService(),
        UserService(),
        AccountService(),
        TransactionService(),
        CategoryService(),
        SplitExpenseService(),
        SettlementService(),
        BudgetService(),
        AnalyticsService(),
    ]
    assert len(services) == 9
