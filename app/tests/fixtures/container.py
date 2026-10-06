import pytest

from deps import init_deps
from deps.container import DIContainer


@pytest.fixture
def di_container() -> DIContainer:
    """Testing dependency container."""
    return init_deps()
