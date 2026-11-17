"""Authentication Pydantic schemas placeholder."""

from pydantic import BaseModel, ConfigDict


class AuthBaseSchema(BaseModel):
    """Base schema for authentication representations."""

    model_config = ConfigDict(from_attributes=True)
