"""Accounts Pydantic schemas placeholder."""

from pydantic import BaseModel, ConfigDict


class AccountBaseSchema(BaseModel):
    """Base schema for account representations."""

    model_config = ConfigDict(from_attributes=True)
