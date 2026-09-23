from datetime import date, datetime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field

from config import settings


class User(BaseModel):
    """User data"""

    id: int
    uuid: UUID
    nickname: str = Field(description='User nickname')
    email: str = Field(description='User email')
    password: str
    date_birth: date | None = Field(default=None, description='Date of birth user')
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(settings.default_timezone),
        description='Date of registration user',
    )
    about: str | None = Field(default=None, description='Information about yourself')
