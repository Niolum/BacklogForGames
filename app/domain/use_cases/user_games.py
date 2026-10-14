from uuid import UUID

from dependency_injector.wiring import Provide, inject

from domain.interfaces.uow import UnitOfWork
from domain.models import UserGamePage, UserGameStatus


@inject
async def get_user_backlog(
    user_uuid: UUID,
    *,
    limit: int,
    offset: int,
    uow: UnitOfWork = Provide['uow'],
) -> UserGamePage:
    """Return one page of a user's backlog."""
    return await _user_games(user_uuid, UserGameStatus.backlog, limit=limit, offset=offset, uow=uow)


@inject
async def get_user_completed(
    user_uuid: UUID,
    *,
    limit: int,
    offset: int,
    uow: UnitOfWork = Provide['uow'],
) -> UserGamePage:
    """Return one page of a user's completed games."""
    return await _user_games(user_uuid, UserGameStatus.completed, limit=limit, offset=offset, uow=uow)


async def _user_games(
    user_uuid: UUID,
    status: UserGameStatus,
    *,
    limit: int,
    offset: int,
    uow: UnitOfWork,
) -> UserGamePage:
    """Load the user and one page of the requested list."""
    async with uow:
        user = await uow.users.get_by_uuid_or_raise(user_uuid)
        return await uow.user_games.get_page(user_id=user.id, status=status, limit=limit, offset=offset)
