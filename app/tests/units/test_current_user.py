from uuid import uuid4

import pytest

from deps.container import DIContainer
from domain.exceptions import AuthError, UserNotFoundError
from domain.services.auth.tokens import create_access_token


async def test_get_current_user_returns_token_owner(di_container: DIContainer, access_token: str) -> None:
    """A valid access token resolves to the user who logged in."""
    user = await di_container.auth_service().get_current_user(access_token)

    assert user.email == 'user@mail.ru'
    assert user.email_confirmed is True


async def test_get_current_user_rejects_invalid_token(di_container: DIContainer) -> None:
    """A broken token is rejected."""
    with pytest.raises(AuthError, match='Invalid token'):
        await di_container.auth_service().get_current_user('not-a-token')


async def test_get_current_user_rejects_unknown_subject(di_container: DIContainer) -> None:
    """A token for a missing user is rejected."""
    user_uuid = uuid4()
    token = create_access_token(user_uuid)

    with pytest.raises(UserNotFoundError, match=f'User with uuid={user_uuid} not found'):
        await di_container.auth_service().get_current_user(token)
