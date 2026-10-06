from pydantic import BaseModel, Field, field_validator


class GenreBaseData(BaseModel):
    """Name and description sent when a genre is created or edited."""

    name: str = Field(description='Genre name')
    description: str | None = Field(default=None, description='Genre description')

    @field_validator('name')
    @classmethod
    def reject_empty_name(cls, name: str) -> str:
        """An empty name is a bad request."""
        if name == '':
            msg = 'Genre name is empty'
            raise ValueError(msg)
        return name

    @field_validator('description')
    @classmethod
    def empty_description_is_none(cls, description: str | None) -> str | None:
        """An empty description is stored as no description."""
        if description == '':
            return None
        return description


class GenreCreateData(GenreBaseData):
    """Name and description of a new genre."""


class GenreChangeData(GenreBaseData):
    """Name and description edited in the admin panel."""
