"""Categories Pydantic schemas placeholder."""

from pydantic import BaseModel, ConfigDict


class CategoryBaseSchema(BaseModel):
    """Base schema for category representations."""

    model_config = ConfigDict(from_attributes=True)
