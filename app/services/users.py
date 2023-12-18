"""Module with user services"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.users import UserNotFoundError
from app.repositories.users import UserRepository
from app.schemas.users import UserDetail


class UserService:
    """Class Service for User"""

    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    async def get_users(self, async_session: AsyncSession, skip: int, limit: int):
        """Get all users"""
        return await self._repository.get_all(async_session, skip, limit)

    async def get_user_by_id(self, async_session: AsyncSession, user_id: UUID):
        """Get user by id"""
        try:
            user = await self._repository.get_by_id(async_session, user_id)
        except UserNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc)
            )
        return user

    async def create_user(
        self,
        async_session: AsyncSession,
        username: str,
        email: str,
        password: str,
        first_name: str | None,
        last_name: str | None,
        avatar: str | None,
        about: str | None
    ):
        """Create user"""
        user = await self._repository.get_by_email(async_session, email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email={email} is already exists"
            )

        user = await self._repository.get_by_username(async_session, username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with username={username} is already exists"
            )
        return await self._repository.add(
            async_session=async_session,
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            avatar=avatar,
            about=about
        )

    async def update_user(
            self,
            async_session: AsyncSession,
            user_id: UUID,
            data: dict,
            current_user: UserDetail
        ):
        """Update user data"""
        email = data["email"]
        user = await self._repository.get_by_email(async_session, email)
        if user and user != current_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email={email} is already exists"
            )
        username = data["username"]
        user = await self._repository.get_by_username(async_session, username)
        if user and user != current_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with username={username} is already exists"
            )
        return await self._repository.update(async_session, user_id, data)

    async def delete_user(self, async_session: AsyncSession, user_id: UUID):
        """Delete user"""
        return await self._repository.delete_by_id(async_session, user_id)

    async def get_user_by_username(self, async_session: AsyncSession, username: str):
        """Get user by username"""
        return await self._repository.get_by_username(async_session, username)
