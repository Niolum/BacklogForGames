from datetime import date
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, Field


class Game(BaseModel):
    """Catalog game."""

    id: int
    uuid: UUID
    title: str = Field(description='Game title')
    release_date: date | None = Field(default=None, description='Release date')
    cover_url: Path | None = Field(default=None, description='Cover URL')
    description: str | None = Field(default=None, description='Game description')
    metacritic: int | None = Field(default=None, description='Metacritic score')
    developer: str | None = Field(default=None, description='Developer')
    publisher: str | None = Field(default=None, description='Publisher')
    is_published: bool = Field(default=True, description='Published in the catalog')
    external_source: str | None = Field(default=None, description='External catalog source')
    external_id: str | None = Field(default=None, description='External catalog id')
