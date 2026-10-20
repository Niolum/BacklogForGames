from uuid import UUID

from dependency_injector.wiring import Provide, inject

from domain.exceptions import GameNotCompletedError
from domain.interfaces.uow import UnitOfWork
from domain.models import Rating, User, UserGameStatus
from domain.services import RatingService, SetRatingData


@inject
async def set_rating(
    user: User,
    game_uuid: UUID,
    data: SetRatingData,
    uow: UnitOfWork = Provide['uow'],
    rating_service: RatingService = Provide['rating_service'],
) -> Rating:
    """Save the current user's score for a completed game."""
    async with uow:
        game = await uow.games.get_by_uuid_or_raise(game_uuid)
        user_game = await uow.user_games.get_by_user_and_game(user.id, game.id)
        if user_game is None or user_game.status is not UserGameStatus.completed:
            msg = f'Game with uuid={game_uuid} is not completed'
            raise GameNotCompletedError(msg)
        existing = await uow.ratings.get_by_user_and_game(user.id, game.id)
        if existing is None:
            return await rating_service.create_rating(user, game, data.score)
        return await rating_service.update_rating(existing, data.score)
