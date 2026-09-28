from pydantic import BaseModel, Field

from domain.services.auth.fields import EmailField, PasswordField


class UserRegisterRequestSchema(BaseModel):
    """Schema for create new user"""

    email: EmailField = Field(description='Email')
    password: PasswordField = Field(description='Password')
    nickname: str = Field(description='User nickname')


class ConfirmEmailRequestSchema(BaseModel):
    """Schema for confirming an email."""

    token: str = Field(description='Confirmation token')


class ResendConfirmationRequestSchema(BaseModel):
    """Schema for sending the confirmation email again."""

    email: EmailField = Field(description='Email')
