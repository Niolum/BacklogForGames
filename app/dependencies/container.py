from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration

from adapters.databases.in_memory.uow import InMemUnitOfWork
from adapters.databases.sqlalchemy.db import async_session_maker
from adapters.databases.sqlalchemy.uow import SQLAUnitOfWork
from domain.services import AuthService


class DIContainer(DeclarativeContainer):
    """Dependency Injector Container"""

    wiring_config = WiringConfiguration(packages=['domain.use_cases'])

    config = providers.Configuration()

    # Unit of Work
    sqlalchemy_uow = providers.ContextLocalSingleton(
        SQLAUnitOfWork,
        session=providers.Factory(async_session_maker),
    )
    uow = providers.Selector(
        config.environment,
        production=sqlalchemy_uow,
        development=sqlalchemy_uow,
        testing=providers.Factory(InMemUnitOfWork),
    )

    auth_service = providers.Factory(AuthService.factory, uow=uow)
