from pydantic import BaseModel, Field


class Genre(BaseModel):
    """Genre of a game."""

    id: int
    name: str = Field(description='Genre name')
    description: str | None = Field(default=None, description='Genre description')
    external_source: str | None = Field(default=None, description='External catalog source')
    external_id: str | None = Field(default=None, description='External catalog id')
