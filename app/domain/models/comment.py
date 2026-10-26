from datetime import datetime
from pathlib import Path
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field

from config import settings
from domain.constants import COMMENT_TEXT_MAX_LENGTH, COMMENT_TEXT_MIN_LENGTH


class Comment(BaseModel):
    """A user's comment on one game."""

    id: int
    uuid: UUID = Field(description='Comment ID')
    user_id: int = Field(description='User')
    game_id: int = Field(description='Game')
    text: str = Field(
        min_length=COMMENT_TEXT_MIN_LENGTH,
        max_length=COMMENT_TEXT_MAX_LENGTH,
        description='Comment text',
    )
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(settings.default_timezone),
        description='Record creation time',
    )
    updated_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(settings.default_timezone),
        description='Record update time',
    )


class CommentAuthor(BaseModel):
    """Author shown with a comment."""

    uuid: UUID = Field(description='User ID')
    nickname: str = Field(description='User nickname')
    avatar_url: Path | None = Field(default=None, description='User avatar URL')


class CommentItem(BaseModel):
    """Comment on a game page."""

    uuid: UUID = Field(description='Comment ID')
    text: str = Field(description='Comment text')
    created_at: AwareDatetime = Field(description='Record creation time')
    updated_at: AwareDatetime = Field(description='Record update time')
    author: CommentAuthor


class CommentPage(BaseModel):
    """One page of comments on a game."""

    items: list[CommentItem]
    total: int
