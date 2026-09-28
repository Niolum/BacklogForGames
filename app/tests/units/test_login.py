import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from dependencies.container import DIContainer
from domain.exceptions import AuthError
from domain.services.auth.tokens import decode_access_token
from domain.services.auth.types import LoginData


async def test_login_rejects_unconfirmed_user(di_container: DIContainer, confirmation_token: str) -> None:
    """A correct password does not issue a token until the email is confirmed."""
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    assert confirmation_token

    with pytest.raises(AuthError, match='Email is not confirmed'):
        await di_container.auth_service().login(LoginData(email='user@mail.ru', password='secret'))


async def test_login_rejects_wrong_password(di_container: DIContainer, confirmation_token: str) -> None:
    """A wrong password is rejected."""
    assert confirmation_token

    with pytest.raises(AuthError, match='Invalid email or password'):
        await di_container.auth_service().login(LoginData(email='user@mail.ru', password='wrong'))


async def test_login_rejects_unknown_email(di_container: DIContainer) -> None:
    """An unknown email is rejected the same way as a wrong password."""
    with pytest.raises(AuthError, match='Invalid email or password'):
        await di_container.auth_service().login(LoginData(email='missing@mail.ru', password='secret'))


async def test_login_returns_token_for_confirmed_user(di_container: DIContainer, confirmation_token: str) -> None:
    """A confirmed user receives a token that carries their uuid."""
    await di_container.auth_service().confirm_email(confirmation_token)

    token = await di_container.auth_service().login(LoginData(email='User@Mail.RU', password='secret'))

    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    assert decode_access_token(token) == stored.uuid


def test_decode_access_token_rejects_invalid_token() -> None:
    """A broken token is rejected."""
    with pytest.raises(AuthError, match='Invalid token'):
        decode_access_token('not-a-token')
