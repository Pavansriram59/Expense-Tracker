"""Users Pydantic schemas placeholder."""

from pydantic import BaseModel, ConfigDict


class UserBaseSchema(BaseModel):
    """Base schema for user representations."""

    model_config = ConfigDict(from_attributes=True)
