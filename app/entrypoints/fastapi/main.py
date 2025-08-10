from fastapi import FastAPI

from config import settings
from .lifespan import lifespan
from .routers import user_router


app = FastAPI(
    version='1.0.0',
    root_path='/api/v1',
    lifespan=lifespan,
    title=settings.project_name,
)


routers = (
    user_router,
)

for router in routers:
    app.include_router(router)
