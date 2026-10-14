from domain.exceptions import UserGameAlreadyListedError
from domain.interfaces.repositories import GameRepo, UserGameRepo
from domain.models import User, UserGame, UserGameStatus
from domain.services.base import BaseService
from .types import AddUserGameData


class UserGameService(BaseService):
    """Changes to the lists of the user identified by the caller."""

    def __init__(self, user_games: UserGameRepo, games: GameRepo):
        self.user_game_repo: UserGameRepo = user_games
        self.game_repo: GameRepo = games

    async def add_to_backlog(self, user: User, data: AddUserGameData) -> UserGame:
        """Add a game that is not in the user's lists yet."""
        game = await self.game_repo.get_by_uuid_or_raise(data.game_uuid)
        existing = await self.user_game_repo.get_by_user_and_game(user.id, game.id)
        if existing is not None:
            msg = f'Game with uuid={data.game_uuid} is already listed'
            raise UserGameAlreadyListedError(msg)
        user_game = UserGame(
            id=await self.user_game_repo.get_next_id(),
            user_id=user.id,
            game_id=game.id,
            status=UserGameStatus.backlog,
        )
        await self.user_game_repo.create(user_game)
        return user_game
