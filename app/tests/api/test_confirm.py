from datetime import datetime, timedelta
from http import HTTPStatus

from httpx import AsyncClient

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import InMemEmailConfirmationRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from config import settings


async def test_confirm_marks_email_and_consumes_token(client: AsyncClient, confirmation_token: str) -> None:
    """A valid token returns 204, confirms the email and is consumed."""
    response = await client.post('/auth/confirm', json={'token': confirmation_token})

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    confirmation = await InMemEmailConfirmationRepo().get_by_token(confirmation_token)
    assert stored is not None
    assert stored.email_confirmed is True
    assert confirmation is not None
    assert confirmation.used_at is not None


async def test_confirm_rejects_used_token(client: AsyncClient, confirmation_token: str) -> None:
    """Repeating a token returns 400 and does not change the confirmation."""
    first = await client.post('/auth/confirm', json={'token': confirmation_token})
    used_at = (await InMemEmailConfirmationRepo().get_by_token_or_raise(confirmation_token)).used_at

    second = await client.post('/auth/confirm', json={'token': confirmation_token})

    assert first.status_code == HTTPStatus.NO_CONTENT
    assert second.status_code == HTTPStatus.BAD_REQUEST
    assert second.json() == {'detail': 'Confirmation token is invalid'}
    confirmation = await InMemEmailConfirmationRepo().get_by_token(confirmation_token)
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert confirmation is not None
    assert confirmation.used_at == used_at
    assert stored is not None
    assert stored.email_confirmed is True


async def test_confirm_rejects_expired_token(client: AsyncClient, confirmation_token: str) -> None:
    """An expired token returns 400 and leaves the email unconfirmed."""
    confirmation = await InMemEmailConfirmationRepo().get_by_token(confirmation_token)
    assert confirmation is not None
    expired = confirmation.model_copy(
        update={'expires_at': datetime.now(settings.default_timezone) - timedelta(hours=1)},
    )
    await InMemEmailConfirmationRepo().update(expired)

    response = await client.post('/auth/confirm', json={'token': confirmation_token})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Confirmation token is invalid'}
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    confirmation = await InMemEmailConfirmationRepo().get_by_token(confirmation_token)
    assert stored is not None
    assert stored.email_confirmed is False
    assert confirmation is not None
    assert confirmation.used_at is None


async def test_confirm_rejects_unknown_token(client: AsyncClient, confirmation_token: str) -> None:
    """An unknown token returns 400 and leaves the registered email unconfirmed."""
    response = await client.post('/auth/confirm', json={'token': 'missing'})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Confirmation token is invalid'}
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    confirmation = await InMemEmailConfirmationRepo().get_by_token(confirmation_token)
    assert stored is not None
    assert stored.email_confirmed is False
    assert confirmation is not None
    assert confirmation.used_at is None
