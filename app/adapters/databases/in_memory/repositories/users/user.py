from typing import ClassVar, override

from adapters.databases.in_memory.repositories.base import InMemBaseRepo
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
