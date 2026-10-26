from abc import abstractmethod

from domain.interfaces.repositories.base import BaseRepo
from domain.models import UserGame, UserGamePage, UserGameStatus, UserListCounts


class UserGameRepo(BaseRepo):
    """User list repository."""

    @abstractmethod
    async def get_next_id(self) -> int:
        """Get next ID."""

    @abstractmethod
    async def create(self, user_game: UserGame) -> None:
        """Create a list entry."""

    @abstractmethod
    async def get_by_user_and_game(self, user_id: int, game_id: int) -> UserGame | None:
        """Get the user's entry for one game."""

    @abstractmethod
    async def update(self, user_game: UserGame) -> None:
        """Update a list entry."""

    @abstractmethod
    async def delete(self, user_game: UserGame) -> None:
        """Delete a list entry."""

    @abstractmethod
    async def count_by_user(self, user_id: int) -> UserListCounts:
        """Count the user's published backlog and completed games."""

    @abstractmethod
    async def get_page(
        self,
        *,
        user_id: int,
        status: UserGameStatus,
        limit: int,
        offset: int,
    ) -> UserGamePage:
        """Return one page of the user's games in the given list, ordered by title."""
