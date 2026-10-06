import pytest

from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from deps.container import DIContainer
from domain.exceptions import GenreHasGamesError, GenreNameAlreadyTakenError, GenreNotFoundError
from domain.models import Genre
from domain.services import GenreChangeData, GenreCreateData


async def test_create_genre_stores_name_and_description(di_container: DIContainer) -> None:
    """A new genre keeps an empty description as no description."""
    genre = await di_container.genre_service().create_genre(GenreCreateData(name='RPG', description=''))

    stored = await InMemGenreRepo().get_by_id(genre.id)
    assert stored is not None
    assert stored.name == 'RPG'
    assert stored.description is None
    assert stored.external_source is None
    assert stored.external_id is None


async def test_create_genre_rejects_taken_name(di_container: DIContainer, stored_genre: Genre) -> None:
    """A name that is already stored is not saved again."""
    assert stored_genre

    with pytest.raises(GenreNameAlreadyTakenError, match=f'Genre with name={stored_genre.name} already exists'):
        await di_container.genre_service().create_genre(GenreCreateData(name=stored_genre.name))

    assert [genre.name for genre in await InMemGenreRepo().get_all()] == [stored_genre.name]


async def test_create_genre_rejects_empty_name(di_container: DIContainer) -> None:
    """An empty name is not saved."""
    with pytest.raises(ValueError, match='Genre name is empty'):
        await di_container.genre_service().create_genre(GenreCreateData(name=''))

    assert await InMemGenreRepo().get_all() == []


async def test_update_genre_rejects_taken_name(
    di_container: DIContainer,
    stored_genre: Genre,
    stored_strategy_genre: Genre,
) -> None:
    """A name that belongs to another genre is not saved."""
    with pytest.raises(GenreNameAlreadyTakenError, match='Genre with name=Strategy already exists'):
        await di_container.genre_service().update_genre(
            stored_genre.id,
            GenreChangeData(name=stored_strategy_genre.name),
        )

    stored = await InMemGenreRepo().get_by_id(stored_genre.id)
    assert stored is not None
    assert stored.name == 'RPG'


async def test_delete_genre_removes_it(di_container: DIContainer, stored_genre: Genre) -> None:
    """A genre without games is deleted."""
    await di_container.genre_service().delete_genre(stored_genre.id)

    assert await InMemGenreRepo().get_by_id(stored_genre.id) is None


async def test_delete_genre_rejects_genre_used_by_games(di_container: DIContainer, stored_genre: Genre) -> None:
    """A genre that games reference stays stored."""
    InMemGenreRepo.USED_BY_GAMES.add(stored_genre.id)

    message = f'Genre with id={stored_genre.id} cannot be deleted because games use it'
    with pytest.raises(GenreHasGamesError, match=message):
        await di_container.genre_service().delete_genre(stored_genre.id)

    assert await InMemGenreRepo().get_by_id(stored_genre.id) == stored_genre


async def test_delete_genre_rejects_unknown_id(di_container: DIContainer) -> None:
    """An unknown id raises not found."""
    with pytest.raises(GenreNotFoundError, match='Genre with id=1 not found'):
        await di_container.genre_service().delete_genre(1)
