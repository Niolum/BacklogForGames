from http import HTTPStatus

from httpx import AsyncClient

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import InMemEmailConfirmationRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo


async def test_resend_confirmation_creates_another_token(client: AsyncClient, confirmation_token: str) -> None:
    """Resend returns 204, stores a second token and leaves the email unconfirmed."""
    response = await client.post('/auth/resend-confirmation', json={'email': 'User@Mail.RU'})

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    confirmations = list(InMemEmailConfirmationRepo.DB.values())
    extra = [item for item in confirmations if item.token != confirmation_token]
    assert stored is not None
    assert stored.email_confirmed is False
    assert len(extra) == 1
    assert extra[0].used_at is None
    assert all(item.used_at is None for item in confirmations)


async def test_resend_confirmation_rejects_confirmed_email(client: AsyncClient, confirmation_token: str) -> None:
    """A confirmed email returns 400 and does not create another token."""
    confirmed = await client.post('/auth/confirm', json={'token': confirmation_token})

    response = await client.post('/auth/resend-confirmation', json={'email': 'user@mail.ru'})

    assert confirmed.status_code == HTTPStatus.NO_CONTENT
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email user@mail.ru is already confirmed'}
    assert len(InMemEmailConfirmationRepo.DB) == 1


async def test_resend_confirmation_rejects_unknown_email(client: AsyncClient) -> None:
    """An unknown email returns 404."""
    response = await client.post('/auth/resend-confirmation', json={'email': 'missing@mail.ru'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User with email=missing@mail.ru not found'}
    assert InMemUserRepo.DB == {}
    assert InMemEmailConfirmationRepo.DB == {}
