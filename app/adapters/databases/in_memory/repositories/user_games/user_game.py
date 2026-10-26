from typing import ClassVar, override

from adapters.databases.in_memory.repositories.base import InMemBaseRepo
from adapters.databases.in_memory.repositories.games.game import InMemGameRepo
from domain.exceptions import GameNotFoundError, UserGameNotFoundError
from domain.interfaces.repositories import UserGameRepo
from domain.models import Game, UserGame, UserGamePage, UserGameStatus, UserListCounts


class InMemUserGameRepo(InMemBaseRepo[UserGame], UserGameRepo):
    """In-memory user list repository."""

    DB: ClassVar[dict[int, UserGame]] = {}

    @override
    async def create(self, user_game: UserGame) -> None:
        self._store(user_game)

    @override
    async def get_by_user_and_game(self, user_id: int, game_id: int) -> UserGame | None:
        return self._get(user_id=user_id, game_id=game_id)

    @override
    async def update(self, user_game: UserGame) -> None:
        if self._get(id=user_game.id) is None:
            msg = f'User game with id={user_game.id} not found'
            raise UserGameNotFoundError(msg)
        self._update(user_game)

    @override
    async def delete(self, user_game: UserGame) -> None:
        if self._get(id=user_game.id) is None:
            msg = f'User game with id={user_game.id} not found'
            raise UserGameNotFoundError(msg)
        del self.DB[user_game.id]

    @override
    async def count_by_user(self, user_id: int) -> UserListCounts:
        backlog_count = 0
        completed_count = 0
        for entry in self.DB.values():
            if entry.user_id != user_id:
                continue
            game = await InMemGameRepo().get_by_id(entry.game_id)
            if game is None or not game.is_published:
                continue
            if entry.status == UserGameStatus.backlog:
                backlog_count += 1
            elif entry.status == UserGameStatus.completed:
                completed_count += 1
        return UserListCounts(backlog_count=backlog_count, completed_count=completed_count)

    @override
    async def get_page(
        self,
        *,
        user_id: int,
        status: UserGameStatus,
        limit: int,
        offset: int,
    ) -> UserGamePage:
        matched = [entry for entry in self.DB.values() if entry.user_id == user_id and entry.status == status]
        games = [await self._game(entry.game_id) for entry in matched]
        games.sort(key=lambda game: (game.title.casefold(), game.id))
        return UserGamePage(items=games[offset : offset + limit], total=len(games))

    async def _game(self, game_id: int) -> Game:
        game = await InMemGameRepo().get_by_id(game_id)
        if game is None:
            msg = f'Game with id={game_id} not found'
            raise GameNotFoundError(msg)
        return game
