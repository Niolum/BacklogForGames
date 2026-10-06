from fastapi import FastAPI

from config import settings
from deps import init_deps
from .admin import setup_admin
from .exception_handlers import register_exception_handlers
from .routers import auth_router, user_router


init_deps()

app = FastAPI(
    version='1.0.0',
    root_path='/api/v1',
    title=settings.project_name,
)
register_exception_handlers(app)
setup_admin(app)


routers = (
    auth_router,
    user_router,
)

for router in routers:
    app.include_router(router)
