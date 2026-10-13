from datetime import UTC, date, datetime
from http import HTTPMethod
from pathlib import Path

import pytest

from adapters.databases.in_memory.repositories.games.game import InMemGameRepo
from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from adapters.http_fetchers import LocalHttpAPIFetcher
from config import rawg_settings
from deps.container import DIContainer
from domain.constants import RAWG_MAX_PAGE_SIZE, RAWG_SOURCE
from domain.exceptions import BadRequestError, GenreNameAlreadyTakenError
from domain.models import Game, Genre
from domain.use_cases import import_catalog
from tests.fixtures.game import GAME_UUID, SECOND_GAME_UUID


async def test_import_does_not_request_rawg_when_the_limit_is_not_positive(di_container: DIContainer) -> None:
    """A non-positive limit raises before any RAWG request."""
    fetcher = _fetcher(di_container)

    with pytest.raises(BadRequestError, match='Game import limit must be positive'):
        await import_catalog(0)

    assert fetcher.calls == []


async def test_import_stores_one_game_and_its_genre_and_stops(
    di_container: DIContainer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """One run stores the game and its genre, then does not read the next page."""
    metacritic = 91
    genre_id = 5
    game_id = 1
    fetcher = _fetcher(di_container)
    fetcher.add_response(
        HTTPMethod.GET,
        'games',
        _page(
            [
                _listed(game_id, 'Planescape', [genre_id, genre_id], metacritic=metacritic),
                _listed(2, 'Torment', [6]),
            ],
            next_page='https://api.rawg.io/api/games?page=2',
        ),
    )
    _add_genre(fetcher, genre_id, 'RPG', 'Role-playing')
    fetcher.add_response(
        HTTPMethod.GET,
        f'games/{game_id}',
        {
            'id': game_id,
            'description': 'A story',
            'developers': [
                {'id': 3, 'name': 'Black Isle'},
                {'id': 8, 'name': 'Ignored'},
            ],
            'publishers': [{'id': 4, 'name': 'Interplay'}],
        },
    )

    with caplog.at_level('INFO', logger='backlogs_domain'):
        await import_catalog(1)

    assert [call.path for call in fetcher.calls] == ['games', f'genres/{genre_id}', f'games/{game_id}']
    listed = fetcher.calls[0]
    assert listed.params is not None
    assert listed.params['key'] == rawg_settings.api_key.get_secret_value()
    assert listed.params['page'] == 1
    assert listed.params['page_size'] == 1
    game = await InMemGameRepo().get_by_external(RAWG_SOURCE, str(game_id))
    assert game is not None
    assert game.title == 'Planescape'
    assert game.release_date == date(1999, 12, 6)
    assert game.cover_url is None
    assert game.description == 'A story'
    assert game.metacritic == metacritic
    assert game.developer == 'Black Isle'
    assert game.publisher == 'Interplay'
    assert game.is_published is True
    assert game.external_source == RAWG_SOURCE
    assert game.external_id == str(game_id)
    assert [(genre.name, genre.description, genre.external_source, genre.external_id) for genre in game.genres] == [
        ('RPG', 'Role-playing', RAWG_SOURCE, str(genre_id)),
    ]
    assert await InMemGameRepo().get_by_external(RAWG_SOURCE, '2') is None
    assert 'RAWG import created 1 games, updated 0 games, created 1 genres' in caplog.text


async def test_import_reads_another_page_until_the_limit(di_container: DIContainer) -> None:
    """A short page is followed by the next page until the limit, and no further."""
    limit = 3
    first_genre_id = 5
    second_genre_id = 6
    skipped_genre_id = 7
    fetcher = _fetcher(di_container)
    fetcher.add_response(
        HTTPMethod.GET,
        'games',
        _page(
            [
                _listed(1, 'Planescape', [first_genre_id]),
                _listed(2, 'Torment', [first_genre_id], released=None, metacritic=None),
            ],
            next_page='https://api.rawg.io/api/games?page=2',
        ),
    )
    fetcher.add_response(
        HTTPMethod.GET,
        'games',
        _page(
            [
                _listed(3, 'Disco', [second_genre_id]),
                _listed(4, 'Skipped', [skipped_genre_id]),
            ],
            next_page='https://api.rawg.io/api/games?page=3',
        ),
    )
    _add_genre(fetcher, first_genre_id, 'RPG', 'Role-playing')
    _add_genre(fetcher, second_genre_id, 'Adventure', None)
    fetcher.add_response(HTTPMethod.GET, 'games/1', {'id': 1, 'description': 'A story'})
    fetcher.add_response(
        HTTPMethod.GET,
        'games/2',
        {'id': 2, 'description': '', 'developers': [], 'publishers': []},
    )
    fetcher.add_response(HTTPMethod.GET, 'games/3', {'id': 3, 'description': 'A world'})

    await import_catalog(limit)

    list_calls = [call for call in fetcher.calls if call.path == 'games']
    second_page = 2
    assert len(list_calls) == second_page
    assert list_calls[0].params is not None
    assert list_calls[0].params['page_size'] == limit
    assert list_calls[1].params is not None
    assert list_calls[1].params['page'] == second_page
    assert list_calls[1].params['page_size'] == 1
    paths = [call.path for call in fetcher.calls]
    assert f'genres/{skipped_genre_id}' not in paths
    assert 'games/4' not in paths
    torment = await InMemGameRepo().get_by_external(RAWG_SOURCE, '2')
    assert torment is not None
    assert torment.release_date is None
    assert torment.metacritic is None
    assert torment.description is None
    assert torment.developer is None
    assert torment.publisher is None
    assert await InMemGameRepo().get_by_external(RAWG_SOURCE, '4') is None
    assert await InMemGameRepo().get_by_external(RAWG_SOURCE, '3') is not None


async def test_import_page_size_is_not_larger_than_the_rawg_maximum(di_container: DIContainer) -> None:
    """The requested page is not larger than the RAWG page size or the remaining limit."""
    fetcher = _fetcher(di_container)
    fetcher.add_response(HTTPMethod.GET, 'games', _page([_listed(1, 'Planescape', [])], next_page=None))
    fetcher.add_response(HTTPMethod.GET, 'games/1', {'id': 1, 'description': 'A story'})

    await import_catalog(RAWG_MAX_PAGE_SIZE + 1)

    listed = fetcher.calls[0]
    assert listed.params is not None
    assert listed.params['page_size'] == RAWG_MAX_PAGE_SIZE
    assert len([call for call in fetcher.calls if call.path == 'games']) == 1


async def test_import_stops_when_the_page_is_empty(di_container: DIContainer) -> None:
    """An empty page ends the import even when RAWG offers a next link."""
    fetcher = _fetcher(di_container)
    fetcher.add_response(HTTPMethod.GET, 'games', _page([], next_page='https://api.rawg.io/api/games?page=2'))

    await import_catalog(1)

    assert len(fetcher.calls) == 1
    assert InMemGameRepo.DB == {}
    assert InMemGenreRepo.DB == {}


async def test_import_reuses_a_genre_that_already_has_the_rawg_pair(di_container: DIContainer) -> None:
    """A genre that already has the RAWG pair is not requested again."""
    genre_id = 5
    existing = Genre(
        id=4,
        name='RPG',
        description='Role-playing',
        external_source=RAWG_SOURCE,
        external_id=str(genre_id),
    )
    await InMemGenreRepo().create(existing)
    fetcher = _fetcher(di_container)
    fetcher.add_response(HTTPMethod.GET, 'games', _page([_listed(1, 'Planescape', [genre_id])], next_page=None))
    fetcher.add_response(HTTPMethod.GET, 'games/1', {'id': 1, 'description': 'A story'})

    await import_catalog(1)

    assert [call.path for call in fetcher.calls] == ['games', 'games/1']
    game = await InMemGameRepo().get_by_external(RAWG_SOURCE, '1')
    assert game is not None
    assert [genre.id for genre in game.genres] == [existing.id]
    assert len(InMemGenreRepo.DB) == 1


async def test_import_stamps_the_rawg_pair_on_a_genre_with_the_same_name(di_container: DIContainer) -> None:
    """A genre with the same name and no external pair receives the RAWG pair."""
    genre_id = 5
    existing = Genre(id=1, name='RPG', description='Role-playing')
    await InMemGenreRepo().create(existing)
    fetcher = _fetcher(di_container)
    fetcher.add_response(HTTPMethod.GET, 'games', _page([_listed(1, 'Planescape', [genre_id])], next_page=None))
    _add_genre(fetcher, genre_id, 'RPG', 'From RAWG')
    fetcher.add_response(HTTPMethod.GET, 'games/1', {'id': 1, 'description': 'A story'})

    await import_catalog(1)

    stored = await InMemGenreRepo().get_by_id(existing.id)
    assert stored is not None
    assert stored.description == 'Role-playing'
    assert stored.external_source == RAWG_SOURCE
    assert stored.external_id == str(genre_id)
    assert len(InMemGenreRepo.DB) == 1


async def test_import_rejects_a_genre_name_owned_by_another_external_pair(di_container: DIContainer) -> None:
    """A taken name that already has an external pair does not create a second genre."""
    genre_id = 5
    other_external_id = '9'
    existing = Genre(
        id=1,
        name='RPG',
        description='Role-playing',
        external_source=RAWG_SOURCE,
        external_id=other_external_id,
    )
    await InMemGenreRepo().create(existing)
    fetcher = _fetcher(di_container)
    fetcher.add_response(HTTPMethod.GET, 'games', _page([_listed(1, 'Planescape', [genre_id])], next_page=None))
    _add_genre(fetcher, genre_id, 'RPG', 'From RAWG')

    with pytest.raises(GenreNameAlreadyTakenError, match='Genre with name=RPG already exists'):
        await import_catalog(1)

    assert await InMemGenreRepo().get_by_id(existing.id) == existing
    assert InMemGameRepo.DB == {}


async def test_import_updates_the_rawg_game_and_leaves_other_games(di_container: DIContainer) -> None:
    """A second run updates the RAWG game and leaves a game without that pair unchanged."""
    moment = datetime(2026, 10, 9, tzinfo=UTC)
    cover = Path('covers/keep.png')
    manual = Game(
        id=1,
        uuid=GAME_UUID,
        title='Planescape',
        created_at=moment,
        updated_at=moment,
    )
    imported = Game(
        id=2,
        uuid=SECOND_GAME_UUID,
        title='Old title',
        cover_url=cover,
        is_published=False,
        external_source=RAWG_SOURCE,
        external_id='7',
        created_at=moment,
        updated_at=moment,
    )
    await InMemGameRepo().create(manual)
    await InMemGameRepo().create(imported)
    fetcher = _fetcher(di_container)
    fetcher.add_response(
        HTTPMethod.GET,
        'games',
        _page([_listed(7, 'New title', [], released='1999-12-06', metacritic=91)], next_page=None),
    )
    fetcher.add_response(HTTPMethod.GET, 'games/7', {'id': 7, 'description': 'A story'})

    await import_catalog(1)

    assert await InMemGameRepo().get_by_id(manual.id) == manual
    stored = await InMemGameRepo().get_by_external(RAWG_SOURCE, '7')
    assert stored is not None
    assert stored.id == imported.id
    assert stored.uuid == SECOND_GAME_UUID
    assert stored.title == 'New title'
    assert stored.cover_url == cover
    assert stored.is_published is False
    assert stored.created_at == moment
    assert stored.updated_at != moment
    stored_games = 2
    assert len(InMemGameRepo.DB) == stored_games


def _fetcher(di_container: DIContainer) -> LocalHttpAPIFetcher:
    """Return the local fetcher selected for tests."""
    fetcher = di_container.http_fetcher()
    if not isinstance(fetcher, LocalHttpAPIFetcher):
        msg = 'Tests use the local HTTP fetcher'
        raise TypeError(msg)
    return fetcher


def _page(results: list[dict[str, object]], *, next_page: str | None) -> dict[str, object]:
    return {'count': len(results), 'next': next_page, 'previous': None, 'results': results}


def _listed(
    game_id: int,
    name: str,
    genre_ids: list[int],
    *,
    released: str | None = '1999-12-06',
    metacritic: int | None = 91,
) -> dict[str, object]:
    return {
        'id': game_id,
        'name': name,
        'released': released,
        'background_image': 'https://example.test/cover.jpg',
        'metacritic': metacritic,
        'genres': [{'id': genre_id} for genre_id in genre_ids],
    }


def _add_genre(fetcher: LocalHttpAPIFetcher, genre_id: int, name: str, description: str | None) -> None:
    fetcher.add_response(
        HTTPMethod.GET,
        f'genres/{genre_id}',
        {'id': genre_id, 'name': name, 'description': description},
    )
