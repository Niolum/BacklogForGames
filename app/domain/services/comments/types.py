from pydantic import BaseModel, Field

from domain.constants import COMMENT_TEXT_MAX_LENGTH, COMMENT_TEXT_MIN_LENGTH


class CreateCommentData(BaseModel):
    """Text of a comment the current user leaves on a game."""

    text: str = Field(
        min_length=COMMENT_TEXT_MIN_LENGTH,
        max_length=COMMENT_TEXT_MAX_LENGTH,
        description='Comment text',
    )
