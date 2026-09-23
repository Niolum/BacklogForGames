from pydantic import BaseModel, Field


class UserBaseData(BaseModel):
    """Base User data"""

    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=32)


class CreateUserData(UserBaseData):
    """Model for create user"""

    nickname: str = Field(..., max_length=255)
