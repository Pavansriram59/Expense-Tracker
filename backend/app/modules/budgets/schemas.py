"""Budgets Pydantic schemas placeholder."""

from pydantic import BaseModel, ConfigDict


class BudgetBaseSchema(BaseModel):
    """Base schema for budget representations."""

    model_config = ConfigDict(from_attributes=True)
