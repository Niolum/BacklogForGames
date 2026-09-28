from http import HTTPStatus

from httpx import AsyncClient

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from domain.services.auth.tokens import decode_access_token


async def test_login_rejects_unconfirmed_user(client: AsyncClient, confirmation_token: str) -> None:
    """An unconfirmed user receives 401."""
    assert confirmation_token

    response = await client.post('/auth/login', json={'email': 'user@mail.ru', 'password': 'secret'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Email is not confirmed'}


async def test_login_rejects_wrong_password(client: AsyncClient, confirmation_token: str) -> None:
    """A wrong password receives 401."""
    assert confirmation_token

    response = await client.post('/auth/login', json={'email': 'user@mail.ru', 'password': 'wrong'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid email or password'}


async def test_login_rejects_unknown_email(client: AsyncClient) -> None:
    """An unknown email receives 401."""
    response = await client.post('/auth/login', json={'email': 'missing@mail.ru', 'password': 'secret'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid email or password'}


async def test_login_returns_token_for_confirmed_user(client: AsyncClient, confirmation_token: str) -> None:
    """A confirmed user receives a bearer token."""
    confirmed = await client.post('/auth/confirm', json={'token': confirmation_token})

    response = await client.post('/auth/login', json={'email': 'User@Mail.RU', 'password': 'secret'})

    assert confirmed.status_code == HTTPStatus.NO_CONTENT
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['token_type'] == 'bearer'
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    assert decode_access_token(body['access_token']) == stored.uuid
