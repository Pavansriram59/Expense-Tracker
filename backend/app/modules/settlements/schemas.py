"""Settlements Pydantic schemas placeholder."""

from pydantic import BaseModel, ConfigDict


class SettlementBaseSchema(BaseModel):
    """Base schema for settlement representations."""

    model_config = ConfigDict(from_attributes=True)
