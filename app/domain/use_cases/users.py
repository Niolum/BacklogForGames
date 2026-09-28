from uuid import UUID

from dependency_injector.wiring import Provide, inject

from domain.interfaces.uow import UnitOfWork
from domain.models import User


@inject
async def get_user_by_uuid(
    user_uuid: UUID,
    uow: UnitOfWork = Provide['uow'],
) -> User:
    """Load a user by the public uuid."""
    async with uow:
        return await uow.users.get_by_uuid_or_raise(user_uuid)
