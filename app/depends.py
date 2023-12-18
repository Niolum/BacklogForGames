"""Dependency Injection File"""


from app.repositories.users import UserRepository
from app.services.users import UserService
from app.services.auth import AuthService
from app.services.database import DatabaseSessionManager


# DB

sessionmanager = DatabaseSessionManager()

# repository - work with DB

user_repo = UserRepository()

# service - work with Services

auth_service = AuthService(user_repo)
user_service = UserService(user_repo)


def get_auth_service():
    """Function return AuthService"""
    return auth_service


def get_user_service():
    """Function return UserService"""
    return user_service


async def get_db():
    """Function for work with DatabaseSessionManager"""
    async with sessionmanager.session() as session:
        yield session
