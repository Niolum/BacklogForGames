from pydantic import BaseModel, Field


class GameGenre(BaseModel):
    """Link between a game and a genre."""

    game_id: int = Field(description='Game')
    genre_id: int = Field(description='Genre')
