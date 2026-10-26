from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, Field

from entrypoints.fastapi.schemas.response.genre import GenreResponseSchema


class UserGameItemResponseSchema(BaseModel):
    """Game shown in a user's backlog or completed list."""

    uuid: UUID = Field(description='Game ID')
    cover_url: Path | None = Field(default=None, description='Cover URL')
    title: str = Field(description='Game title')
    genres: list[GenreResponseSchema] = Field(default_factory=list, description='Genres of the game')


class UserGamePageResponseSchema(BaseModel):
    """One page of a user's backlog."""

    items: list[UserGameItemResponseSchema] = Field(description='Games on this page')
    total: int = Field(description='Number of games in this list')


class CompletedGameItemResponseSchema(UserGameItemResponseSchema):
    """Completed game and the list owner's score."""

    user_score: int | None = Field(description='Score of the list owner')


class CompletedGamePageResponseSchema(BaseModel):
    """One page of a user's completed games."""

    items: list[CompletedGameItemResponseSchema] = Field(description='Games on this page')
    total: int = Field(description='Number of games in this list')
