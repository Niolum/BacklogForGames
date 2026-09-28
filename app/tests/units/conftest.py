import pytest

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import InMemEmailConfirmationRepo
from dependencies.container import DIContainer
from domain.services.auth.types import CreateUserData


@pytest.fixture
async def confirmation_token(di_container: DIContainer, clear_repositories: None) -> str:
    """Token issued by registering a user through the auth service after the store is cleared."""
    del clear_repositories
    await di_container.auth_service().register_user(
        CreateUserData(email='user@mail.ru', password='secret', nickname='nick'),
    )
    return next(iter(InMemEmailConfirmationRepo.DB.values())).token
