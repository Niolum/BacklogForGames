import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.models import User
from domain.services.auth.types import CreateUserData


ADMIN_EMAIL = 'admin@mail.ru'
ADMIN_PASSWORD = 'secret'


@pytest.fixture
async def admin_user(di_container: DIContainer, clear_repositories: None) -> User:
    """Confirmed administrator stored in the in-memory user repository."""
    del clear_repositories
    await di_container.auth_service().register_user(
        CreateUserData(email=ADMIN_EMAIL, password=ADMIN_PASSWORD, nickname='admin'),
    )
    stored = await InMemUserRepo().get_by_email(ADMIN_EMAIL)
    assert stored is not None
    admin = stored.model_copy(update={'is_admin': True, 'email_confirmed': True})
    await InMemUserRepo().update(admin)
    return admin
