from abc import abstractmethod
from uuid import UUID

from domain.exceptions import GameNotFoundError
from domain.interfaces.repositories.base import BaseRepo
from domain.models import Game, GamePage


class GameRepo(BaseRepo):
    """Game repository."""

    @abstractmethod
    async def get_next_id(self) -> int:
        """Get next ID."""

    @abstractmethod
    async def create(self, game: Game) -> None:
        """Create a game and store its genres."""

    @abstractmethod
    async def get_by_id(self, game_id: int) -> Game | None:
        """Get by id."""

    async def get_by_id_or_raise(self, game_id: int) -> Game:
        """Get by id or raise exception."""
        game = await self.get_by_id(game_id)
        if game is None:
            msg = f'Game with id={game_id} not found'
            raise GameNotFoundError(msg)
        return game

    @abstractmethod
    async def get_by_uuid(self, game_uuid: UUID) -> Game | None:
        """Get by uuid."""

    async def get_by_uuid_or_raise(self, game_uuid: UUID) -> Game:
        """Get by uuid or raise exception."""
        game = await self.get_by_uuid(game_uuid)
        if game is None:
            msg = f'Game with uuid={game_uuid} not found'
            raise GameNotFoundError(msg)
        return game

    @abstractmethod
    async def update(self, game: Game) -> None:
        """Update a game and replace its genres."""

    @abstractmethod
    async def get_page(
        self,
        *,
        genre_id: int | None = None,
        query: str | None = None,
        limit: int,
        offset: int,
    ) -> GamePage:
        """Return published games, filtered by genre and title, one page at a time."""
