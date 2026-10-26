from pydantic import BaseModel, Field

from domain.constants import COMMENT_TEXT_MAX_LENGTH, COMMENT_TEXT_MIN_LENGTH


class CreateCommentRequestSchema(BaseModel):
    """Text sent by the current user."""

    text: str = Field(
        min_length=COMMENT_TEXT_MIN_LENGTH,
        max_length=COMMENT_TEXT_MAX_LENGTH,
        description='Comment text',
    )
