"""Module for create FastAPI application"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import AdminAuth
from app.admin.models import UserAdmin
from app.settings import setting
from app.depends import sessionmanager, get_user_service, get_auth_service


def init_app(init_db=True):
    """Function create FastAPI application"""

    lifespan = None # type: ignore

    if init_db:
        sessionmanager.init(setting.DB_CONFIG)
        user_service = get_user_service()
        auth_service = get_auth_service()

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            username = setting.USERNAME
            email = setting.EMAIL
            password = setting.PASSWORD
            first_name = setting.FIRST_NAME
            last_name = setting.LAST_NAME
            avatar = setting.AVATAR
            about = setting.ABOUT
            is_superuser = setting.IS_SUPERUSER
            async with sessionmanager.session() as session:
                try:
                    hashed_password = auth_service.get_password_hash(password)
                    await user_service.create_user(
                        session,
                        username,
                        email,
                        hashed_password,
                        first_name,
                        last_name,
                        avatar,
                        about,
                        is_superuser
                    )
                except Exception:
                    print("Admin has been already register")
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    server = FastAPI(title="BacklogGames", lifespan=lifespan)

    from app.endpoints.users import user_router, auth_router

    server.include_router(auth_router, prefix="/api")
    server.include_router(user_router, prefix="/api")

    authentication_back = AdminAuth(sessionmanager, secret_key=setting.SECRET_KEY)
    admin = Admin(server, sessionmanager._engine, authentication_backend=authentication_back)
    admin.add_view(UserAdmin)

    return server
