from typing import ClassVar, override
from uuid import UUID

from adapters.databases.in_memory.repositories.base import InMemBaseRepo
from domain.exceptions import NotFoundError
from domain.interfaces.repositories import UserRepo
from domain.models import User


class InMemUserRepo(InMemBaseRepo[User], UserRepo):
    """In-memory user repository"""

    DB: ClassVar[dict[int, User]] = {}

    @override
    async def create(self, user: User) -> None:
        self._store(user)

    @override
    async def get_by_email(self, email: str) -> User | None:
        return self._get(email=email)

    @override
    async def get_by_id(self, user_id: int) -> User | None:
        return self._get(id=user_id)

    @override
    async def get_by_uuid(self, user_uuid: UUID) -> User | None:
        return self._get(uuid=user_uuid)

    @override
    async def get_by_nickname(self, nickname: str) -> User | None:
        return self._get(nickname=nickname)

    @override
    async def update(self, user: User) -> None:
        if self._get(id=user.id) is None:
            msg = f'User with id={user.id} not found'
            raise NotFoundError(msg)
        self._update(user)
