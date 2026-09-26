from pydantic import BaseModel, Field

from domain.services.auth.fields import EmailField, PasswordField


class UserRegisterRequestSchema(BaseModel):
    """Schema for create new user"""

    email: EmailField = Field(description='Email')
    password: PasswordField = Field(description='Password')
    nickname: str = Field(description='User nickname')
