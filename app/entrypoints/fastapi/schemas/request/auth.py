from pydantic import BaseModel, Field, field_validator


class UserRegisterRequestSchema(BaseModel):
    """Schema for create new user"""

    email: str = Field(..., max_length=255, description='Email')
    password: str = Field(..., max_length=128, description='Password')
    nickname: str = Field(description='User nickname')

    @field_validator('email', mode='before')
    @classmethod
    def email_lower(cls, v: str) -> str:
        """Email to lowercase"""
        return v.lower() if isinstance(v, str) else v
