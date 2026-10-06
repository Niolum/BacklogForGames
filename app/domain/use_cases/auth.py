from uuid import UUID

from dependency_injector.wiring import Provide, inject

from domain.interfaces.uow import UnitOfWork
from domain.models import User
from domain.services import AuthService, CreateUserData, LoginData


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
async def login(
    user_data: LoginData,
    uow: UnitOfWork = Provide['uow'],
    auth_service: 'AuthService' = Provide['auth_service'],
) -> str:
    """Issue an access token."""
    async with uow:
        return await auth_service.login(user_data)


@inject
async def authenticate_admin(
    user_data: LoginData,
    uow: UnitOfWork = Provide['uow'],
    auth_service: 'AuthService' = Provide['auth_service'],
) -> User | None:
    """Return the administrator when the email and password are valid."""
    async with uow:
        return await auth_service.authenticate_admin(user_data)


@inject
async def get_admin_user(
    user_uuid: UUID,
    uow: UnitOfWork = Provide['uow'],
    auth_service: 'AuthService' = Provide['auth_service'],
) -> User | None:
    """Load the administrator stored in the admin session."""
    async with uow:
        return await auth_service.get_admin_user(user_uuid)


@inject
async def get_current_user(
    token: str,
    uow: UnitOfWork = Provide['uow'],
    auth_service: 'AuthService' = Provide['auth_service'],
) -> User:
    """Load the user identified by an access token."""
    async with uow:
        return await auth_service.get_current_user(token)


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
