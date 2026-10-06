from abc import abstractmethod

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

    @abstractmethod
    async def get_by_name(self, name: str) -> Genre | None:
        """Get by name."""

    @abstractmethod
    async def get_all(self) -> list[Genre]:
        """Return all genres ordered by id."""

    @abstractmethod
    async def update(self, genre: Genre) -> None:
        """Update a genre."""

    @abstractmethod
    async def delete(self, genre: Genre) -> None:
        """Delete a genre."""
