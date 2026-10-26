from uuid import UUID

from dependency_injector.wiring import Provide, inject

from domain.interfaces.uow import UnitOfWork
from domain.models import CompletedGame, CompletedGamePage, User, UserGame, UserGamePage, UserGameStatus
from domain.services import AddUserGameData, UserGameService


@inject
async def get_user_backlog(
    user_uuid: UUID,
    *,
    limit: int,
    offset: int,
    uow: UnitOfWork = Provide['uow'],
) -> UserGamePage:
    """Return one page of a user's backlog."""
    async with uow:
        user = await uow.users.get_by_uuid_or_raise(user_uuid)
        return await uow.user_games.get_page(user_id=user.id, status=UserGameStatus.backlog, limit=limit, offset=offset)


@inject
async def get_user_completed(
    user_uuid: UUID,
    *,
    limit: int,
    offset: int,
    uow: UnitOfWork = Provide['uow'],
) -> CompletedGamePage:
    """Return one page of a user's completed games and that user's score for each game."""
    async with uow:
        user = await uow.users.get_by_uuid_or_raise(user_uuid)
        page = await uow.user_games.get_page(
            user_id=user.id,
            status=UserGameStatus.completed,
            limit=limit,
            offset=offset,
        )
        items: list[CompletedGame] = []
        for game in page.items:
            rating = await uow.ratings.get_by_user_and_game(user.id, game.id)
            user_score = None if rating is None else rating.score
            items.append(CompletedGame(game=game, user_score=user_score))
        return CompletedGamePage(items=items, total=page.total)


@inject
async def add_to_backlog(
    user: User,
    data: AddUserGameData,
    uow: UnitOfWork = Provide['uow'],
    user_game_service: UserGameService = Provide['user_game_service'],
) -> UserGame:
    """Add a game to the current user's backlog."""
    async with uow:
        return await user_game_service.add_to_backlog(user, data)


@inject
async def add_to_completed(
    user: User,
    data: AddUserGameData,
    uow: UnitOfWork = Provide['uow'],
    user_game_service: UserGameService = Provide['user_game_service'],
) -> UserGame:
    """Mark a game completed for the current user."""
    async with uow:
        return await user_game_service.add_to_completed(user, data)


@inject
async def remove_from_list(
    user: User,
    game_uuid: UUID,
    uow: UnitOfWork = Provide['uow'],
    user_game_service: UserGameService = Provide['user_game_service'],
) -> None:
    """Remove a game from the current user's backlog or completed list."""
    async with uow:
        await user_game_service.remove_from_list(user, game_uuid)
