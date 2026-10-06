import pytest

from dependencies import init_deps
from dependencies.container import DIContainer


@pytest.fixture
def di_container() -> DIContainer:
    """Testing dependency container."""
    return init_deps()
