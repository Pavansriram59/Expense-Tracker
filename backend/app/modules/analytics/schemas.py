"""Analytics Pydantic schemas placeholder."""

from pydantic import BaseModel, ConfigDict


class AnalyticsBaseSchema(BaseModel):
    """Base schema for analytics representations."""

    model_config = ConfigDict(from_attributes=True)
