"""User repositories module"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User 

class UserRepository:
    """Class for work """

    def __init__(self, async_session: AsyncSession) -> None:
        self.async_session = async_session

    async def get_all(self, skip: int = 0, limit: int = 100):
        """Getting all users"""
        result = await self.async_session.execute(
            select(User)
            .order_by(User.username)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().fetchall()

    async def get_by_id(self, user_id: str) -> User:
        """Getting user by id"""
        result = await self.async_session.execute(
            select(User)
            .where(User.id==user_id)
        )
        user = result.scalars().first()
        if not user:
            raise UserNotFoundError(user_id)
        return user


    async def add(self, username: str, email: str, password: str, first_name: str | None, last_name: str | None, avatar: str | None):
        """Create user"""
        user = User(
            username=username,
            hashed_password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            avatar=avatar
        )
        self.async_session.add(user)
        await self.async_session.commit()
        await self.async_session.refresh(user)
        return user

    async def delete_by_id(self, user_id: str):
        """Delete user"""
        result = await self.async_session.execute(
            select(User)
            .where(User.id==user_id)
        )
        user = result.scalars().first()
        if not user:
            raise UserNotFoundError(user_id)
        await self.async_session.delete(user)
        await self.async_session.commit()


class NotFoundError(Exception):

    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class UserNotFoundError(NotFoundError):

    entity_name: str = "User"