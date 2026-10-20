from datetime import datetime

from pydantic import AwareDatetime, BaseModel, Field

from config import settings


class Rating(BaseModel):
    """A user's score for one game."""

    id: int
    user_id: int = Field(description='User')
    game_id: int = Field(description='Game')
    score: int = Field(ge=1, le=10, description='Score from 1 to 10')
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(settings.default_timezone),
        description='Record creation time',
    )
    updated_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(settings.default_timezone),
        description='Record update time',
    )
