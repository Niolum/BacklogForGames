from uuid import UUID

from dependency_injector.wiring import Provide, inject

from domain.interfaces.uow import UnitOfWork
from domain.models import User
from domain.services import UpdateProfileData, UserService


@inject
async def get_user_by_uuid(
    user_uuid: UUID,
    uow: UnitOfWork = Provide['uow'],
) -> User:
    """Load a user by the public uuid."""
    async with uow:
        return await uow.users.get_by_uuid_or_raise(user_uuid)


@inject
async def upload_avatar(
    user: User,
    content: bytes,
    content_type: str | None,
    uow: UnitOfWork = Provide['uow'],
    user_service: UserService = Provide['user_service'],
) -> User:
    """Store an avatar for the given user."""
    async with uow:
        return await user_service.upload_avatar(user, content, content_type)


@inject
async def delete_avatar(
    user: User,
    uow: UnitOfWork = Provide['uow'],
    user_service: UserService = Provide['user_service'],
) -> None:
    """Remove the avatar of the given user."""
    async with uow:
        await user_service.delete_avatar(user)


@inject
async def update_profile(
    user: User,
    data: UpdateProfileData,
    uow: UnitOfWork = Provide['uow'],
    user_service: UserService = Provide['user_service'],
) -> User:
    """Update the profile that belongs to the given user."""
    async with uow:
        return await user_service.update_profile(user, data)
