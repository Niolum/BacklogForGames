from uuid import uuid4

from domain.exceptions import AuthError
from domain.interfaces.repositories import UserRepo
from domain.models.user import User
from domain.services.base import BaseService
from .types import CreateUserData
from .utils import hash_password


class AuthService(BaseService):
    """Service authentication for management registration, authentication and update tokens"""

    def __init__(self, users: UserRepo):
        self.user_repo = users

    async def register_user(self, user_data: CreateUserData) -> None:
        """Register new user"""
        db_user = await self.user_repo.get_by_email(user_data.email)
        if db_user:
            msg = f'User with email={user_data.email} already exists'
            raise AuthError(msg)

        next_id = await self.user_repo.get_next_id()
        hashed_password = hash_password(user_data.password)

        user = User(
            id=next_id,
            uuid=uuid4(),
            nickname=user_data.nickname,
            email=user_data.email,
            password=hashed_password,
        )

        await self.user_repo.create(user)
