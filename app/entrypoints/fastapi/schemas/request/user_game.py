from uuid import UUID

from pydantic import BaseModel, Field


class AddUserGameRequestSchema(BaseModel):
    """Game the current user adds to a list."""

    game_uuid: UUID = Field(description='Game ID')
