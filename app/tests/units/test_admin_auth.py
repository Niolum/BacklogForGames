from uuid import uuid4

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.models import User
from domain.services.auth.types import LoginData
from tests.fixtures.admin import ADMIN_EMAIL, ADMIN_PASSWORD


async def test_authenticate_admin_returns_confirmed_admin(di_container: DIContainer, admin_user: User) -> None:
    """A confirmed administrator is accepted."""
    user = await di_container.auth_service().authenticate_admin(
        LoginData(email='Admin@Mail.RU', password=ADMIN_PASSWORD),
    )

    assert user is not None
    assert user.uuid == admin_user.uuid


async def test_authenticate_admin_rejects_non_admin(di_container: DIContainer, confirmation_token: str) -> None:
    """A confirmed user without the admin flag is rejected."""
    await di_container.auth_service().confirm_email(confirmation_token)

    user = await di_container.auth_service().authenticate_admin(
        LoginData(email='user@mail.ru', password='secret'),
    )

    assert user is None


async def test_authenticate_admin_rejects_unconfirmed_admin(di_container: DIContainer, admin_user: User) -> None:
    """An administrator with an unconfirmed email is rejected."""
    await InMemUserRepo().update(admin_user.model_copy(update={'email_confirmed': False}))

    user = await di_container.auth_service().authenticate_admin(
        LoginData(email=ADMIN_EMAIL, password=ADMIN_PASSWORD),
    )

    assert user is None


async def test_authenticate_admin_rejects_wrong_password(di_container: DIContainer, admin_user: User) -> None:
    """A wrong password is rejected."""
    assert admin_user

    user = await di_container.auth_service().authenticate_admin(
        LoginData(email=ADMIN_EMAIL, password='wrong'),
    )

    assert user is None


async def test_authenticate_admin_rejects_unknown_email(di_container: DIContainer) -> None:
    """An unknown email is rejected."""
    user = await di_container.auth_service().authenticate_admin(
        LoginData(email='missing@mail.ru', password=ADMIN_PASSWORD),
    )

    assert user is None


async def test_get_admin_user_returns_admin(di_container: DIContainer, admin_user: User) -> None:
    """The session user is loaded while the admin flag is set."""
    user = await di_container.auth_service().get_admin_user(admin_user.uuid)

    assert user is not None
    assert user.id == admin_user.id


async def test_get_admin_user_rejects_revoked_admin(di_container: DIContainer, admin_user: User) -> None:
    """Clearing the admin flag closes the session user."""
    await InMemUserRepo().update(admin_user.model_copy(update={'is_admin': False}))

    user = await di_container.auth_service().get_admin_user(admin_user.uuid)

    assert user is None


async def test_get_admin_user_rejects_unknown_uuid(di_container: DIContainer) -> None:
    """An unknown session id does not open the panel."""
    user = await di_container.auth_service().get_admin_user(uuid4())

    assert user is None
