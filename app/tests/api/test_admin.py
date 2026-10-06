from http import HTTPStatus

from httpx import AsyncClient

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from domain.models import User
from tests.fixtures.admin import ADMIN_EMAIL, ADMIN_PASSWORD


async def test_admin_login_rejects_non_admin(client: AsyncClient, access_token: str) -> None:
    """A confirmed user without the admin flag stays on the login page."""
    assert access_token

    response = await client.post(
        '/admin/login',
        data={'email': 'user@mail.ru', 'password': 'secret'},
    )
    panel = await client.get('/admin/')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Invalid credentials.' in response.text
    assert panel.status_code == HTTPStatus.FOUND


async def test_admin_login_rejects_unconfirmed_admin(client: AsyncClient, admin_user: User) -> None:
    """An unconfirmed administrator cannot open the panel."""
    await InMemUserRepo().update(admin_user.model_copy(update={'email_confirmed': False}))

    response = await client.post(
        '/admin/login',
        data={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Invalid credentials.' in response.text


async def test_admin_login_rejects_wrong_password(client: AsyncClient, admin_user: User) -> None:
    """A wrong password does not open the panel."""
    assert admin_user

    response = await client.post(
        '/admin/login',
        data={'email': ADMIN_EMAIL, 'password': 'wrong'},
    )
    panel = await client.get('/admin/')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert panel.status_code == HTTPStatus.FOUND


async def test_admin_login_rejects_invalid_email(client: AsyncClient) -> None:
    """A value that is not an email does not open the panel."""
    response = await client.post(
        '/admin/login',
        data={'email': 'not-an-email', 'password': ADMIN_PASSWORD},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
