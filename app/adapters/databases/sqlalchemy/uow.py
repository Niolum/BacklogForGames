from typing import override

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from adapters.databases.sqlalchemy import repositories
from domain.interfaces.uow import UnitOfWork


class SQLAUnitOfWork(UnitOfWork):
    """Unit of Work для работы с SQLAlchemy."""

    _model_changes: list
    transaction: AsyncSessionTransaction

    def __init__(self, session: AsyncSession):
        self.session = session

        for repo_name, repo_class in UnitOfWork.__annotations__.items():
            if not str(repo_class).endswith('Repo'):
                continue

            repo_impl = getattr(repositories, f'SQLA{repo_class}')
            repo_instance = repo_impl(session)
            setattr(self, repo_name, repo_instance)

    @override
    async def begin(self) -> None:
        await self.session.begin()

    @override
    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        """Откат транзакции в базе данных."""
        await self.session.rollback()

    async def __aenter__(self):
        self.transaction = await self.session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transaction.__aexit__(exc_type, exc_val, exc_tb)
