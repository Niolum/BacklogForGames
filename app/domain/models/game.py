from datetime import date, datetime
from pathlib import Path
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field

from config import settings
from domain.models.genre import Genre


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
    genres: list[Genre] = Field(default_factory=list, description='Genres of the game')
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(settings.default_timezone),
        description='Record creation time',
    )
    updated_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(settings.default_timezone),
        description='Record update time',
    )


class GamePage(BaseModel):
    """One page of games and the total number of matches."""

    items: list[Game]
    total: int
