from pydantic import BaseModel, Field


class LoginResponseSchema(BaseModel):
    """Access token issued at login."""

    access_token: str = Field(description='JWT access token')
    token_type: str = Field(default='bearer', description='Token type')
