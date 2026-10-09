from typing import ClassVar, override
from uuid import UUID

from adapters.databases.in_memory.repositories.base import InMemBaseRepo
from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from domain.exceptions import GameNotFoundError, GenreNotFoundError
from domain.interfaces.repositories import GameRepo
from domain.models import Game, GamePage, Genre


class InMemGameRepo(InMemBaseRepo[Game], GameRepo):
    """In-memory game repository."""

    DB: ClassVar[dict[int, Game]] = {}

    @override
    async def create(self, game: Game) -> None:
        self._store(game.model_copy(update={'genres': await self._genres(game.genres)}))

    @override
    async def get_by_id(self, game_id: int) -> Game | None:
        return self._get(id=game_id)

    @override
    async def get_by_uuid(self, game_uuid: UUID) -> Game | None:
        return self._get(uuid=game_uuid)

    @override
    async def update(self, game: Game) -> None:
        if self._get(id=game.id) is None:
            msg = f'Game with id={game.id} not found'
            raise GameNotFoundError(msg)
        self._update(game.model_copy(update={'genres': await self._genres(game.genres)}))

    @override
    async def get_page(
        self,
        *,
        genre_id: int | None = None,
        query: str | None = None,
        limit: int,
        offset: int,
    ) -> GamePage:
        matched = [game for game in self.DB.values() if self._matches(game, genre_id, query)]
        matched.sort(key=lambda game: game.title.casefold())
        return GamePage(items=matched[offset : offset + limit], total=len(matched))

    async def _genres(self, genres: list[Genre]) -> list[Genre]:
        stored: dict[int, Genre] = {}
        for genre in genres:
            found = await InMemGenreRepo().get_by_id(genre.id)
            if found is None:
                msg = f'Genre with id={genre.id} not found'
                raise GenreNotFoundError(msg)
            stored.setdefault(genre.id, found)
        return [stored[genre_id] for genre_id in sorted(stored)]

    def _matches(self, game: Game, genre_id: int | None, query: str | None) -> bool:
        if not game.is_published:
            return False
        if genre_id is not None and all(genre.id != genre_id for genre in game.genres):
            return False
        return query is None or query == '' or query.casefold() in game.title.casefold()
