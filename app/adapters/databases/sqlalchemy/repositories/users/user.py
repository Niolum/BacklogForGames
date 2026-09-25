from typing import override

from sqlalchemy import select, text

from adapters.databases.sqlalchemy.models import UserORM
from adapters.databases.sqlalchemy.repositories.base import SQLABaseRepo
from domain.interfaces.repositories import UserRepo
from domain.models import User


class SQLAUserRepo(SQLABaseRepo, UserRepo):
    """Реализация репозитория пользователей на SQLAlchemy."""

    @override
    async def get_next_id(self) -> int:
        res = await self.session.execute(text("select nextval('users_id_seq')"))
        return res.scalar_one()

    @override
    async def create(self, user: User) -> None:
        user_orm = UserORM(**user.model_dump())
        self.session.add(user_orm)
        await self.session.flush()
        await self.session.refresh(user_orm)

    @override
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(UserORM).where(UserORM.email == email))
        user_orm = result.scalar_one_or_none()
        if not user_orm:
            return None
        return user_orm.to_domain()
