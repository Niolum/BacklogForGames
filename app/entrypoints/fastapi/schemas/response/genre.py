from pydantic import BaseModel, Field


class GenreResponseSchema(BaseModel):
    """Genre visible to anyone."""

    id: int = Field(description='Genre id')
    name: str = Field(description='Genre name')
    description: str | None = Field(default=None, description='Genre description')
