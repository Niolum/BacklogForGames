from pydantic import BaseModel, Field


class SetRatingData(BaseModel):
    """Score the current user sets for one game."""

    score: int = Field(ge=1, le=10, description='Score from 1 to 10')
