import pytest

from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from domain.exceptions import NotFoundError
from domain.models import Genre


async def test_genre_repo_finds_genre_by_id_and_name(genre: Genre) -> None:
    """The repository returns the same genre by id and name."""
    repo = InMemGenreRepo()
    await repo.create(genre)

    assert await repo.get_by_id(genre.id) == genre
    assert await repo.get_by_name(genre.name) == genre
    assert await repo.get_by_id(99) is None
    assert await repo.get_by_name('missing') is None


async def test_genre_repo_lists_genres_by_id(genre: Genre, strategy_genre: Genre) -> None:
    """The list contains every stored genre, ordered by id."""
    repo = InMemGenreRepo()
    await repo.create(strategy_genre)
    await repo.create(genre)

    genres = await repo.get_all()

    assert [item.name for item in genres] == ['RPG', 'Strategy']


async def test_genre_repo_updates_existing_genre(genre: Genre) -> None:
    """Update replaces the stored genre and keeps the same id."""
    repo = InMemGenreRepo()
    await repo.create(genre)

    await repo.update(genre.model_copy(update={'name': 'Adventure', 'description': None}))

    stored = await repo.get_by_id(genre.id)
    assert stored is not None
    assert stored.name == 'Adventure'
    assert stored.description is None
    assert await repo.get_by_name('RPG') is None
    assert await repo.get_by_name('Adventure') == stored


async def test_genre_repo_update_missing_genre_raises(genre: Genre) -> None:
    """Update of an unknown id raises not found."""
    repo = InMemGenreRepo()

    with pytest.raises(NotFoundError, match='Genre with id=1 not found'):
        await repo.update(genre)


async def test_genre_repo_deletes_genre(genre: Genre, strategy_genre: Genre) -> None:
    """Delete removes the genre from id and name lookup."""
    repo = InMemGenreRepo()
    await repo.create(genre)
    await repo.create(strategy_genre)

    await repo.delete(genre)

    assert await repo.get_by_id(genre.id) is None
    assert await repo.get_by_name('RPG') is None
    assert [item.name for item in await repo.get_all()] == ['Strategy']


async def test_genre_repo_delete_missing_genre_raises(genre: Genre) -> None:
    """Delete of an unknown id raises not found."""
    repo = InMemGenreRepo()

    with pytest.raises(NotFoundError, match='Genre with id=1 not found'):
        await repo.delete(genre)


async def test_genre_repo_get_next_id_follows_the_highest_id(genre: Genre) -> None:
    """The next id is one greater than the highest stored id."""
    repo = InMemGenreRepo()
    assert await repo.get_next_id() == 1

    await repo.create(genre)

    assert await repo.get_next_id() == genre.id + 1
