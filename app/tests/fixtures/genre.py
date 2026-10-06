import pytest

from domain.models import Genre


@pytest.fixture
def genre() -> Genre:
    """Genre used as the stored record in repository tests."""
    return Genre(id=1, name='RPG', description='Role-playing')


@pytest.fixture
def strategy_genre() -> Genre:
    """Second genre with a higher id."""
    return Genre(id=2, name='Strategy')
