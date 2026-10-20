from pydantic import BaseModel, Field


class RatingResponseSchema(BaseModel):
    """Score saved for the current user."""

    score: int = Field(ge=1, le=10, description='Score from 1 to 10')
