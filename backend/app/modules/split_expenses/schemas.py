"""Split Expenses Pydantic schemas placeholder."""

from pydantic import BaseModel, ConfigDict


class SplitExpenseBaseSchema(BaseModel):
    """Base schema for split expense representations."""

    model_config = ConfigDict(from_attributes=True)
