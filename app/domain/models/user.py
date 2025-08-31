from datetime import date
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field


class User(BaseModel):
    """User data"""

    id: int
    uuid: UUID
    nickname: str = Field(description='User nickname')
    email: str = Field(description='User email')
    password: str
    date_birth: date | None = Field(default=None, description='Date of birth user')
    created_at: AwareDatetime = Field(description='Date of registration user')
    about: str | None = Field(default=None, description='Information about yourself')
