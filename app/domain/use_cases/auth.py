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


@inject
async def resend_confirmation_email(
    email: str,
    uow: UnitOfWork = Provide['uow'],
    auth_service: 'AuthService' = Provide['auth_service'],
) -> None:
    """Send another confirmation link for an unconfirmed email."""
    async with uow:
        await auth_service.resend_confirmation_email(email)


@inject
async def confirm_email(
    token: str,
    uow: UnitOfWork = Provide['uow'],
    auth_service: 'AuthService' = Provide['auth_service'],
) -> None:
    """Confirm user email by token"""
    async with uow:
        await auth_service.confirm_email(token)
