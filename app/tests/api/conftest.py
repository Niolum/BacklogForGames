from http import HTTPStatus

import pytest
from httpx import ASGITransport, AsyncClient

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import InMemEmailConfirmationRepo
from entrypoints.fastapi.main import app


@pytest.fixture
async def client():
    """HTTP client for the application backed by the in-memory unit of work."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as http_client:
        yield http_client


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
