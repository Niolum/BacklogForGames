from abc import abstractmethod

from domain.exceptions import GenreNotFoundError
from domain.interfaces.repositories.base import BaseRepo
from domain.models import Genre


class GenreRepo(BaseRepo):
    """Genre repository."""

    @abstractmethod
    async def get_next_id(self) -> int:
        """Get next ID."""

    @abstractmethod
    async def create(self, genre: Genre) -> None:
        """Create a genre."""

    @abstractmethod
    async def get_by_id(self, genre_id: int) -> Genre | None:
        """Get by id."""

    async def get_by_id_or_raise(self, genre_id: int) -> Genre:
        """Get by id or raise exception."""
        genre = await self.get_by_id(genre_id)
        if genre is None:
            msg = f'Genre with id={genre_id} not found'
            raise GenreNotFoundError(msg)
        return genre

    @abstractmethod
    async def get_by_name(self, name: str) -> Genre | None:
        """Get by name."""

    @abstractmethod
    async def has_games(self, genre_id: int) -> bool:
        """Return whether any game references this genre."""

    @abstractmethod
    async def get_all(self) -> list[Genre]:
        """Return all genres ordered by id."""

    @abstractmethod
    async def update(self, genre: Genre) -> None:
        """Update a genre."""

    @abstractmethod
    async def delete(self, genre: Genre) -> None:
        """Delete a genre."""
