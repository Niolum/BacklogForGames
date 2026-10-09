from datetime import date
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, Field

from entrypoints.fastapi.schemas.response.genre import GenreResponseSchema


class GameResponseSchema(BaseModel):
    """Published game visible in the catalog."""

    uuid: UUID = Field(description='Game ID')
    title: str = Field(description='Game title')
    release_date: date | None = Field(default=None, description='Release date')
    cover_url: Path | None = Field(default=None, description='Cover URL')
    description: str | None = Field(default=None, description='Game description')
    metacritic: int | None = Field(default=None, description='Metacritic score')
    developer: str | None = Field(default=None, description='Developer')
    publisher: str | None = Field(default=None, description='Publisher')
    genres: list[GenreResponseSchema] = Field(default_factory=list, description='Genres of the game')


class GamePageResponseSchema(BaseModel):
    """One page of published games."""

    items: list[GameResponseSchema] = Field(description='Games on this page')
    total: int = Field(description='Number of published games that match the filters')
