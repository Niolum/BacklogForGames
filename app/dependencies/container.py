from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration

from adapters.database.db import async_session_maker
from adapters.database.uow import SQLAUnitOfWork
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
        testing=sqlalchemy_uow,
    )

    auth_service = providers.Factory(AuthService.factory, uow=uow)
