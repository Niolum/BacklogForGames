from pathlib import Path

from pydantic import BaseModel, Field

from entrypoints.fastapi.schemas.response.genre import GenreResponseSchema


class UserGameItemResponseSchema(BaseModel):
    """Game shown in a user's backlog or completed list."""

    cover_url: Path | None = Field(default=None, description='Cover URL')
    title: str = Field(description='Game title')
    genres: list[GenreResponseSchema] = Field(default_factory=list, description='Genres of the game')


class UserGamePageResponseSchema(BaseModel):
    """One page of a user's backlog or completed list."""

    items: list[UserGameItemResponseSchema] = Field(description='Games on this page')
    total: int = Field(description='Number of games in this list')
