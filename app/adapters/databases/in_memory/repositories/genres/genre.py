from typing import ClassVar, override

from adapters.databases.in_memory.repositories.base import InMemBaseRepo
from domain.exceptions import GenreNotFoundError
from domain.interfaces.repositories import GenreRepo
from domain.models import Genre


class InMemGenreRepo(InMemBaseRepo[Genre], GenreRepo):
    """In-memory genre repository."""

    DB: ClassVar[dict[int, Genre]] = {}

    @override
    async def create(self, genre: Genre) -> None:
        self._store(genre)

    @override
    async def get_by_id(self, genre_id: int) -> Genre | None:
        return self._get(id=genre_id)

    @override
    async def get_by_name(self, name: str) -> Genre | None:
        return self._get(name=name)

    @override
    async def has_games(self, genre_id: int) -> bool:
        from adapters.databases.in_memory.repositories.games.game import InMemGameRepo

        return any(genre.id == genre_id for game in InMemGameRepo.DB.values() for genre in game.genres)

    @override
    async def get_all(self) -> list[Genre]:
        return [self.DB[genre_id] for genre_id in sorted(self.DB)]

    @override
    async def update(self, genre: Genre) -> None:
        if self._get(id=genre.id) is None:
            msg = f'Genre with id={genre.id} not found'
            raise GenreNotFoundError(msg)
        self._update(genre)

    @override
    async def delete(self, genre: Genre) -> None:
        if self._get(id=genre.id) is None:
            msg = f'Genre with id={genre.id} not found'
            raise GenreNotFoundError(msg)
        del self.DB[genre.id]
