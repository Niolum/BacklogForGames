import contextlib
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from config import settings


class DatabaseSessionManager:
    """DB sessions manager"""

    def __init__(self, db_url: str, engine_kwargs: dict[str, Any]) -> None:
        self._engine: AsyncEngine | None = create_async_engine(db_url, **engine_kwargs)
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = async_sessionmaker(
            autocommit=False,
            bind=self._engine,
        )

    @staticmethod
    def _raise_exception(msg: str) -> None:
        raise Exception(msg)

    def _validate_session(self) -> bool:
        is_valid = True
        if not self._engine:
            is_valid = False
        if self._sessionmaker is None:
            is_valid = False
        return is_valid

    async def close(self) -> None:
        """Close session"""
        is_valid = self._validate_session()
        if not is_valid:
            msg = 'DatabaseSessionManager is not initialized'
            self._raise_exception(msg)

        await self._engine.dispose()  # type: ignore [union-attr]

        self._engine = None
        self._sessionmaker = None


    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncGenerator[AsyncConnection]:
        """Connect to db"""
        is_valid = self._validate_session()
        if not is_valid:
            msg = 'DatabaseSessionManager is not initialized'
            self._raise_exception(msg)

        async with self._engine.begin() as connection:  # type: ignore [union-attr]
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        """Session iterator"""
        is_valid = self._validate_session()
        if not is_valid:
            msg = 'DatabaseSessionManager is not initialized'
            self._raise_exception(msg)

        session = self._sessionmaker()  # type: ignore
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


session_manager = DatabaseSessionManager(str(settings.db_alembic_url), {'echo': settings.db_echo})


async def get_db_session():
    """Get db session"""
    async with session_manager.session() as session:
        yield session
