from datetime import date

from pydantic import BaseModel, Field, field_validator


class GameFormData(BaseModel):
    """Fields the admin panel sends when a game is created or edited."""

    title: str = Field(description='Game title')
    release_date: date | None = Field(default=None, description='Release date')
    description: str | None = Field(default=None, description='Game description')
    metacritic: int | None = Field(default=None, description='Metacritic score')
    developer: str | None = Field(default=None, description='Developer')
    publisher: str | None = Field(default=None, description='Publisher')
    is_published: bool = Field(default=True, description='Published in the catalog')
    genres: list[int] = Field(default_factory=list, description='Genre ids')

    @field_validator('title')
    @classmethod
    def reject_empty_title(cls, title: str) -> str:
        """An empty title is a bad request."""
        if title == '':
            msg = 'Game title is empty'
            raise ValueError(msg)
        return title

    @field_validator('description', 'developer', 'publisher')
    @classmethod
    def empty_text_is_none(cls, value: str | None) -> str | None:
        """An empty text is stored as no text."""
        if value == '':
            return None
        return value

    @field_validator('release_date', 'metacritic', mode='before')
    @classmethod
    def empty_optional_is_none(cls, value: object) -> object:
        """An empty optional field is stored as no value."""
        if value == '':
            return None
        return value

    @field_validator('genres', mode='before')
    @classmethod
    def genre_ids(cls, genres: object) -> list[int]:
        """The form sends genre ids."""
        if genres is None:
            return []
        if isinstance(genres, list):
            return [int(genre_id) for genre_id in genres]
        if isinstance(genres, int | str):
            return [int(genres)]
        msg = 'Genres are invalid'
        raise ValueError(msg)


class GameCreateData(GameFormData):
    """Fields of a new game."""


class GameChangeData(GameFormData):
    """Fields edited in the admin panel."""
