import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.models import User
from domain.services.auth.types import CreateUserData


@pytest.fixture
async def registered_user(di_container: DIContainer, clear_repositories: None) -> User:
    """Registered user stored in the in-memory repository."""
    del clear_repositories
    await di_container.auth_service().register_user(
        CreateUserData(email='user@mail.ru', password='secret', nickname='nick'),
    )
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    return stored
