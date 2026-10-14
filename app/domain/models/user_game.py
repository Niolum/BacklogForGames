from datetime import datetime
from enum import StrEnum, auto
from typing import Self

from pydantic import AwareDatetime, BaseModel, Field, model_validator

from config import settings
from domain.models.game import Game


class UserGameStatus(StrEnum):
    """Place of a game in a user's lists."""

    backlog = auto()
    completed = auto()


class UserGame(BaseModel):
    """A game in one user's backlog or completed list."""

    id: int
    user_id: int = Field(description='User')
    game_id: int = Field(description='Game')
    status: UserGameStatus = Field(description='List status')
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(settings.default_timezone),
        description='Record creation time',
    )
    completed_at: AwareDatetime | None = Field(default=None, description='Completion time')

    @model_validator(mode='after')
    def backlog_has_empty_completed_at(self) -> Self:
        """A backlog row has no completion time."""
        if self.status is UserGameStatus.backlog and self.completed_at is not None:
            msg = 'Backlog status requires an empty completed_at'
            raise ValueError(msg)
        return self


class UserGamePage(BaseModel):
    """One page of a user's list and the total number of matches."""

    items: list[Game]
    total: int
