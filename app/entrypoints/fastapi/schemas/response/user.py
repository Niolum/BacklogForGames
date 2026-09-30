from datetime import date
from pathlib import Path
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field


class PublicUserResponseSchema(BaseModel):
    """Profile visible to anyone."""

    uuid: UUID = Field(description='User ID')
    nickname: str = Field(description='User nickname')
    date_birth: date | None = Field(default=None, description='Date of birth user')
    created_at: AwareDatetime = Field(description='Date of registration user')
    about: str | None = Field(default=None, description='Information about yourself')
    avatar_url: Path | None = Field(default=None, description='User avatar URL')


class UserMeResponseSchema(PublicUserResponseSchema):
    """Profile of the current user."""

    email: str = Field(description='User email')
    email_confirmed: bool = Field(description='Email confirmation flag')
