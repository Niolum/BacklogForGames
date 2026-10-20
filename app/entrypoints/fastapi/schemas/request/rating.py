from pydantic import BaseModel, Field


class SetRatingRequestSchema(BaseModel):
    """Score sent by the current user."""

    score: int = Field(ge=1, le=10, description='Score from 1 to 10')
