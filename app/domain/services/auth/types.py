from pydantic import BaseModel, Field

from .fields import EmailField, PasswordField


class UserBaseData(BaseModel):
    """Base User data"""

    email: EmailField
    password: PasswordField


class CreateUserData(UserBaseData):
    """Model for create user"""

    nickname: str = Field(..., max_length=255)
