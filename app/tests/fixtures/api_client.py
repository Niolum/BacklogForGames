import pytest
from httpx import ASGITransport, AsyncClient

from entrypoints.fastapi.main import app


@pytest.fixture
async def client():
    """HTTP client for the application backed by the in-memory unit of work."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as http_client:
        yield http_client
