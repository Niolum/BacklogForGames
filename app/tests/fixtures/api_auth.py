from http import HTTPStatus

import pytest
from httpx import AsyncClient

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import (
    InMemEmailConfirmationRepo,
)
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo


@pytest.fixture
async def confirmation_token(client: AsyncClient, clear_repositories: None) -> str:
    """Token issued by registering a user after the store is cleared."""
    del clear_repositories
    response = await client.post(
        '/auth/register',
        json={'email': 'user@mail.ru', 'password': 'secret', 'nickname': 'nick'},
    )
    assert response.status_code == HTTPStatus.CREATED
    return next(iter(InMemEmailConfirmationRepo.DB.values())).token


@pytest.fixture
async def access_token(client: AsyncClient, confirmation_token: str) -> str:
    """Access token of the registered user after the email is confirmed."""
    confirmed = await client.post('/auth/confirm', json={'token': confirmation_token})
    assert confirmed.status_code == HTTPStatus.NO_CONTENT
    response = await client.post('/auth/login', json={'email': 'user@mail.ru', 'password': 'secret'})
    assert response.status_code == HTTPStatus.OK
    return response.json()['access_token']


@pytest.fixture
async def other_access_token(client: AsyncClient, access_token: str) -> str:
    """Access token of a second confirmed user."""
    del access_token
    response = await client.post(
        '/auth/register',
        json={'email': 'other@mail.ru', 'password': 'secret', 'nickname': 'other'},
    )
    assert response.status_code == HTTPStatus.CREATED
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None
    confirmation = next(item for item in InMemEmailConfirmationRepo.DB.values() if item.user_id == other.id)
    confirmed = await client.post('/auth/confirm', json={'token': confirmation.token})
    assert confirmed.status_code == HTTPStatus.NO_CONTENT
    login = await client.post('/auth/login', json={'email': 'other@mail.ru', 'password': 'secret'})
    assert login.status_code == HTTPStatus.OK
    return login.json()['access_token']
