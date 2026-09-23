from dependency_injector.wiring import Provide, inject

from domain.interfaces.uow import UnitOfWork
from domain.services import AuthService, CreateUserData


@inject
async def register_user(
    user_data: CreateUserData,
    uow: UnitOfWork = Provide['uow'],
    auth_service: 'AuthService' = Provide['auth_service'],
) -> None:
    """Register new user"""
    async with uow:
        await auth_service.register_user(user_data)
