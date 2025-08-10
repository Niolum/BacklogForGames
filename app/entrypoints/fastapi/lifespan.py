from contextlib import asynccontextmanager

from fastapi import FastAPI

from adapters.database.session import session_manager


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Function that handles startup and shutdown events"""
    yield
    if session_manager._engine is not None:  # noqa: SLF001
        await session_manager.close()
