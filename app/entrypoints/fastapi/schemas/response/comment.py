from pathlib import Path
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field


class CommentAuthorResponseSchema(BaseModel):
    """Author shown with a comment."""

    uuid: UUID = Field(description='User ID')
    nickname: str = Field(description='User nickname')
    avatar_url: Path | None = Field(default=None, description='User avatar URL')


class CommentResponseSchema(BaseModel):
    """Comment returned after it is created."""

    uuid: UUID = Field(description='Comment ID')
    text: str = Field(description='Comment text')
    created_at: AwareDatetime = Field(description='Record creation time')
    updated_at: AwareDatetime = Field(description='Record update time')
    author: CommentAuthorResponseSchema
