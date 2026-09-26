from http import HTTPStatus

import pytest
from httpx import AsyncClient

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo


async def test_register_creates_user(client: AsyncClient) -> None:
    """Registering a new user returns 201 and stores the normalized email."""
    response = await client.post(
        '/auth/register',
        json={'email': 'User@Mail.RU', 'password': 'secret', 'nickname': 'nick'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.content == b''
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    assert stored.nickname == 'nick'
    assert stored.password != 'secret'


async def test_register_rejects_duplicate_email(client: AsyncClient) -> None:
    """A second registration with the same email returns 409."""
    first = await client.post(
        '/auth/register',
        json={'email': 'User@Mail.RU', 'password': 'secret', 'nickname': 'nick'},
    )
    second = await client.post(
        '/auth/register',
        json={'email': 'user@mail.ru', 'password': 'secret', 'nickname': 'other'},
    )

    assert first.status_code == HTTPStatus.CREATED
    assert second.status_code == HTTPStatus.CONFLICT
    assert second.json() == {'detail': 'User with email=user@mail.ru already exists'}


@pytest.mark.parametrize(
    'payload',
    [
        {'email': 'not-an-email', 'password': 'secret', 'nickname': 'nick'},
        {'email': 'user@mail.ru', 'password': 'a' * 73, 'nickname': 'nick'},
        {'email': 'user@mail.ru', 'password': 'secret'},
    ],
)
async def test_register_rejects_invalid_data(client: AsyncClient, payload: dict[str, str]) -> None:
    """Invalid registration data is rejected before a user is created."""
    response = await client.post('/auth/register', json=payload)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert InMemUserRepo.DB == {}
