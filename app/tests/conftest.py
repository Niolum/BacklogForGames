import os
import tempfile


os.environ['APP_CONFIG__ENVIRONMENT'] = 'testing'
os.environ['APP_CONFIG__LOGS_PATH'] = tempfile.mkdtemp(prefix='backlog-test-logs-')

import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo


@pytest.fixture(autouse=True)
def clear_users() -> None:
    """Drop users left in the in-memory repository by a previous test."""
    InMemUserRepo.DB.clear()
