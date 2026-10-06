from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration

from adapters.databases.in_memory.uow import InMemUnitOfWork
from adapters.databases.sqlalchemy.db import async_session_maker
from adapters.databases.sqlalchemy.uow import SQLAUnitOfWork
from adapters.mail import LocalMailSender, SMTPMailSender
from adapters.storage import LocalFileStorage, S3FileStorage
from config import email_settings, storage_settings
from domain.services import AuthService, UserService


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

    local_mail_sender = providers.Singleton(LocalMailSender)
    smtp_mail_sender = providers.Singleton(
        SMTPMailSender,
        host=email_settings.host,
        port=email_settings.port,
        sender=email_settings.from_email,
        username=email_settings.username,
        password=email_settings.password,
    )
    mail_sender = providers.Selector(
        config.environment,
        production=smtp_mail_sender,
        development=local_mail_sender,
        testing=local_mail_sender,
    )
    auth_service = providers.Factory(AuthService.factory, uow=uow, mail_sender=mail_sender)

    local_file_storage = providers.Singleton(LocalFileStorage, root=storage_settings.local_root)
    s3_file_storage = providers.Singleton(
        S3FileStorage,
        bucket=storage_settings.s3_bucket,
        access_key=storage_settings.s3_access_key,
        secret_key=storage_settings.s3_secret_key,
        endpoint_url=storage_settings.s3_endpoint_url,
    )
    file_storage = providers.Selector(
        config.environment,
        production=s3_file_storage,
        development=local_file_storage,
        testing=local_file_storage,
    )
    user_service = providers.Factory(UserService.factory, uow=uow, file_storage=file_storage)
