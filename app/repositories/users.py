"""User repositories module"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.exceptions.users import UserNotFoundError


class UserRepository:
    """Class for work with user in DB"""

    async def get_all(self, async_session: AsyncSession, skip: int = 0, limit: int = 100):
        """Getting all users from DB"""
        result = await async_session.execute(
            select(User)
            .order_by(User.username)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().fetchall()

    async def get_by_id(self, async_session: AsyncSession, user_id: UUID) -> User:
        """Getting user by id from DB"""
        result = await async_session.execute(
            select(User)
            .where(User.id==user_id)
        )
        user = result.scalars().first()
        if not user:
            raise UserNotFoundError(user_id)
        return user

    async def add(
            self,
            async_session: AsyncSession,
            username: str,
            email: str,
            password: str,
            first_name: str | None,
            last_name: str | None,
            avatar: str | None,
            about: str | None,
            is_superuser: bool = False
        ):
        """Create user in DB"""
        user = User(
            username=username,
            hashed_password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            avatar=avatar,
            about=about,
            is_superuser=is_superuser
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        return user

    async def update(self, async_session: AsyncSession, user_id: UUID, data: dict):
        """Update data"""
        user = await self.get_by_id(async_session, user_id)
        for key, value in data.items():
            setattr(user, key, value)
        await async_session.commit()
        await async_session.refresh(user)
        return user

    async def delete_by_id(self, async_session: AsyncSession, user_id: UUID):
        """Delete user from DB"""
        result = await async_session.execute(
            select(User)
            .where(User.id==user_id)
        )
        user = result.scalars().first()
        if not user:
            raise UserNotFoundError(user_id)
        await async_session.delete(user)
        await async_session.commit()

    async def get_by_username(self, async_session: AsyncSession, username: str):
        """Getting by username"""
        result = await async_session.execute(
            select(User)
            .where(User.username==username)
        )
        user = result.scalars().first()
        return user

    async def get_by_email(self, async_session: AsyncSession, email: str):
        """Getting by email"""
        result = await async_session.execute(
            select(User)
            .where(User.email==email)
        )
        user = result.scalars().first()
        return user
