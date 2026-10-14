from uuid import UUID

from pydantic import BaseModel, Field


class AddUserGameData(BaseModel):
    """Game added to the current user's list."""

    game_uuid: UUID = Field(description='Game ID')
