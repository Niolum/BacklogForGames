from http import HTTPStatus

import pytest
from httpx import AsyncClient

from domain.models import User
from tests.fixtures.admin import ADMIN_EMAIL, ADMIN_PASSWORD


@pytest.fixture
async def admin_client(client: AsyncClient, admin_user: User) -> AsyncClient:
    """HTTP client signed in to the admin panel."""
    del admin_user
    response = await client.post(
        '/admin/login',
        data={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD},
    )
    assert response.status_code == HTTPStatus.FOUND
    return client
