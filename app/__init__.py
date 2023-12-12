"""Module for create FastAPI application"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.settings import setting
from app.services.database import sessionmanager


def init_app(init_db=True):
    """Function create FastAPI application"""

    lifespan = None # type: ignore

    if init_db:
        sessionmanager.init(setting.DB_CONFIG)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    server = FastAPI(title="BacklogGames", lifespan=lifespan)

    return server