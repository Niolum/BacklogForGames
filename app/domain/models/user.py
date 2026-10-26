from datetime import date, datetime
from pathlib import Path
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
    avatar_url: Path | None = Field(default=None, description='User avatar URL')
    email_confirmed: bool = Field(default=False, description='Email confirmation flag')
    is_admin: bool = Field(default=False, description='Administrator flag')


class UserListCounts(BaseModel):
    """Sizes of one user's lists. They are counted, not stored on the user."""

    backlog_count: int = Field(description='Number of games in the backlog')
    completed_count: int = Field(description='Number of completed games')


class UserProfile(BaseModel):
    """A user together with the sizes of their lists."""

    user: User
    counts: UserListCounts
