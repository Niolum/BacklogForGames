import pytest

from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from domain.models import Genre


@pytest.fixture
def genre() -> Genre:
    """Genre used as the stored record in repository tests."""
    return Genre(id=1, name='RPG', description='Role-playing')


@pytest.fixture
def strategy_genre() -> Genre:
    """Second genre with a higher id."""
    return Genre(id=2, name='Strategy')


@pytest.fixture
async def stored_genre(genre: Genre, clear_repositories: None) -> Genre:
    """Genre saved in the in-memory repository."""
    del clear_repositories
    await InMemGenreRepo().create(genre)
    return genre


@pytest.fixture
async def stored_strategy_genre(strategy_genre: Genre, clear_repositories: None) -> Genre:
    """Second genre saved in the in-memory repository."""
    del clear_repositories
    await InMemGenreRepo().create(strategy_genre)
    return strategy_genre
