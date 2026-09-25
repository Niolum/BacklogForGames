from typing import override

from domain.interfaces.uow import UnitOfWork


class InMemUnitOfWork(UnitOfWork):
    """Unit of Work for working with an in-memory repository."""

    def __init__(self):
        from adapters.databases.in_memory import repositories

        for repo_name, repo_class in UnitOfWork.__annotations__.items():
            if not str(repo_class).endswith('Repo'):
                continue
            setattr(self, repo_name, getattr(repositories, f'InMem{repo_class}')())

    @override
    async def begin(self):
        pass

    async def commit(self):
        """No commit is required for an in-memory repository."""

    async def rollback(self):
        """Data rollback is not required for the in-memory repository."""
