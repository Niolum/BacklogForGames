import os
import shutil
import tempfile
from pathlib import Path


os.environ['APP_CONFIG__ENVIRONMENT'] = 'testing'
os.environ['APP_CONFIG__LOGS_PATH'] = tempfile.mkdtemp(prefix='backlog-test-logs-')
os.environ['STORAGE_CONFIG__LOCAL_ROOT'] = tempfile.mkdtemp(prefix='backlog-test-storage-')

import pytest

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import (
    InMemEmailConfirmationRepo,
)
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from dependencies import init_deps
from dependencies.container import DIContainer


@pytest.fixture
def di_container() -> DIContainer:
    """Testing dependency container."""
    return init_deps()


@pytest.fixture(autouse=True)
def clear_repositories() -> None:
    """Drop records and local files left by a previous test."""
    InMemUserRepo.DB.clear()
    InMemEmailConfirmationRepo.DB.clear()
    root = Path(os.environ['STORAGE_CONFIG__LOCAL_ROOT'])
    if root.exists():
        shutil.rmtree(root)
    root.mkdir()
