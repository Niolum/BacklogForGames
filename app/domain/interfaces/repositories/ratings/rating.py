from abc import abstractmethod

from domain.interfaces.repositories.base import BaseRepo
from domain.models import Rating, RatingSummary


class RatingRepo(BaseRepo):
    """User score repository."""

    @abstractmethod
    async def get_next_id(self) -> int:
        """Get next ID."""

    @abstractmethod
    async def create(self, rating: Rating) -> None:
        """Create a score."""

    @abstractmethod
    async def get_by_user_and_game(self, user_id: int, game_id: int) -> Rating | None:
        """Get the user's score for one game."""

    @abstractmethod
    async def update(self, rating: Rating) -> None:
        """Update a score."""

    @abstractmethod
    async def get_summary(self, game_id: int) -> RatingSummary:
        """Return the average score and the number of scores for one game."""
