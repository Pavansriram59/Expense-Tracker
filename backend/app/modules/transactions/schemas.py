"""Transactions Pydantic schemas placeholder."""

from pydantic import BaseModel, ConfigDict


class TransactionBaseSchema(BaseModel):
    """Base schema for transaction representations."""

    model_config = ConfigDict(from_attributes=True)
