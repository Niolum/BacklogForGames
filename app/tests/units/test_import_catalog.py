from datetime import UTC, date, datetime
from http import HTTPMethod
from pathlib import Path

import pytest

from adapters.databases.in_memory.repositories.games.game import InMemGameRepo
from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from adapters.http_fetchers import LocalHttpAPIFetcher
from config import rawg_settings, storage_settings
from deps.container import DIContainer
from domain.constants import COVER_MAX_BYTES, RAWG_MAX_PAGE_SIZE, RAWG_SOURCE
from domain.exceptions import BadRequestError, GenreNameAlreadyTakenError
from domain.models import Game, Genre
from domain.use_cases import get_game_by_uuid, get_games, import_catalog
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
    """A second run updates the RAWG row. An unavailable cover leaves the stored file."""
    moment = datetime(2026, 10, 9, tzinfo=UTC)
    metacritic = 91
    genre_id = 5
    cover = Path('covers/keep.png')
    previous = Genre(id=3, name='Strategy')
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
        genres=[previous],
        created_at=moment,
        updated_at=moment,
    )
    await InMemGenreRepo().create(previous)
    await InMemGameRepo().create(manual)
    await InMemGameRepo().create(imported)
    fetcher = _fetcher(di_container)
    fetcher.add_response(
        HTTPMethod.GET,
        'games',
        _page(
            [_listed(7, 'New title', [genre_id], released='1999-12-06', metacritic=metacritic)],
            next_page=None,
        ),
    )
    _add_genre(fetcher, genre_id, 'RPG', 'Role-playing')
    fetcher.add_response(
        HTTPMethod.GET,
        'games/7',
        {
            'id': 7,
            'description': 'A story',
            'developers': [{'id': 3, 'name': 'Black Isle'}, {'id': 8, 'name': 'Ignored'}],
            'publishers': [{'id': 4, 'name': 'Interplay'}],
        },
    )

    await import_catalog(1)

    assert await InMemGameRepo().get_by_id(manual.id) == manual
    stored = await InMemGameRepo().get_by_external(RAWG_SOURCE, '7')
    assert stored is not None
    assert stored.id == imported.id
    assert stored.uuid == SECOND_GAME_UUID
    assert stored.title == 'New title'
    assert stored.release_date == date(1999, 12, 6)
    assert stored.cover_url == cover
    assert stored.metacritic == metacritic
    assert stored.description == 'A story'
    assert stored.developer == 'Black Isle'
    assert stored.publisher == 'Interplay'
    assert [genre.name for genre in stored.genres] == ['RPG']
    assert stored.is_published is False
    assert stored.created_at == moment
    assert stored.updated_at != moment
    stored_games = 2
    assert len(InMemGameRepo.DB) == stored_games


async def test_import_saves_the_cover_and_returns_its_path(di_container: DIContainer) -> None:
    """A supported background image is stored and returned by the list and the card."""
    image_url = 'https://example.test/cover.jpg'
    fetcher = _fetcher(di_container)
    fetcher.add_response(
        HTTPMethod.GET,
        'games',
        _page([_listed(1, 'Planescape', [], background_image=image_url)], next_page=None),
    )
    fetcher.add_response(HTTPMethod.GET, 'games/1', {'id': 1, 'description': 'A story'})
    fetcher.add_download(image_url, b'jpeg-bytes', 'image/jpeg; charset=binary')

    await import_catalog(1)

    stored = await InMemGameRepo().get_by_external(RAWG_SOURCE, '1')
    assert stored is not None
    assert stored.cover_url == Path('covers') / f'{stored.uuid}.jpg'
    assert stored.cover_url is not None
    assert (storage_settings.local_root / stored.cover_url).read_bytes() == b'jpeg-bytes'
    page_limit = 20
    page = await get_games(limit=page_limit, offset=0)
    assert page.items[0].cover_url == stored.cover_url
    card = await get_game_by_uuid(stored.uuid)
    assert card.cover_url == stored.cover_url


async def test_import_replaces_the_previous_cover_file(di_container: DIContainer) -> None:
    """A new cover replaces the stored file and removes the previous one."""
    image_url = 'https://example.test/cover.gif'
    moment = datetime(2026, 10, 9, tzinfo=UTC)
    previous = storage_settings.local_root / 'covers' / 'keep.png'
    previous.parent.mkdir(parents=True)
    previous.write_bytes(b'old')
    imported = Game(
        id=1,
        uuid=GAME_UUID,
        title='Old title',
        cover_url=Path('covers/keep.png'),
        external_source=RAWG_SOURCE,
        external_id='7',
        created_at=moment,
        updated_at=moment,
    )
    await InMemGameRepo().create(imported)
    fetcher = _fetcher(di_container)
    fetcher.add_response(
        HTTPMethod.GET,
        'games',
        _page([_listed(7, 'Planescape', [], background_image=image_url)], next_page=None),
    )
    fetcher.add_response(HTTPMethod.GET, 'games/7', {'id': 7, 'description': 'A story'})
    fetcher.add_download(image_url, b'gif-bytes', 'image/gif')

    await import_catalog(1)

    stored = await InMemGameRepo().get_by_external(RAWG_SOURCE, '7')
    assert stored is not None
    assert stored.cover_url == Path('covers') / f'{GAME_UUID}.gif'
    assert stored.cover_url is not None
    assert (storage_settings.local_root / stored.cover_url).read_bytes() == b'gif-bytes'
    assert not previous.exists()


async def test_import_keeps_the_game_when_the_cover_cannot_be_saved(di_container: DIContainer) -> None:
    """A missing, empty, oversized, or unsupported cover still saves the game."""
    missing_url = None
    fetcher = _fetcher(di_container)
    fetcher.add_response(
        HTTPMethod.GET,
        'games',
        _page(
            [
                _listed(1, 'Planescape', [], background_image=missing_url),
                _listed(2, 'Torment', [], background_image=''),
                _listed(3, 'Disco', [], background_image='https://example.test/notes.txt'),
                _listed(4, 'Empty', [], background_image='https://example.test/empty.jpg'),
                _listed(5, 'Bare', [], background_image='https://example.test/bare.jpg'),
                _listed(6, 'Huge', [], background_image='https://example.test/huge.jpg'),
            ],
            next_page=None,
        ),
    )
    for game_id in range(1, 7):
        fetcher.add_response(HTTPMethod.GET, f'games/{game_id}', {'id': game_id, 'description': 'A story'})
    fetcher.add_download('https://example.test/notes.txt', b'notes', 'text/plain')
    fetcher.add_download('https://example.test/empty.jpg', b'', 'image/jpeg')
    fetcher.add_download('https://example.test/bare.jpg', b'jpeg-bytes', None)
    fetcher.add_download('https://example.test/huge.jpg', b'x' * (COVER_MAX_BYTES + 1), 'image/jpeg')

    limit = 6
    await import_catalog(limit)

    for external_id in ('1', '2', '3', '4', '5', '6'):
        stored = await InMemGameRepo().get_by_external(RAWG_SOURCE, external_id)
        assert stored is not None
        assert stored.cover_url is None


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
    background_image: str | None = 'https://example.test/cover.jpg',
) -> dict[str, object]:
    return {
        'id': game_id,
        'name': name,
        'released': released,
        'background_image': background_image,
        'metacritic': metacritic,
        'genres': [{'id': genre_id} for genre_id in genre_ids],
    }


def _add_genre(fetcher: LocalHttpAPIFetcher, genre_id: int, name: str, description: str | None) -> None:
    fetcher.add_response(
        HTTPMethod.GET,
        f'genres/{genre_id}',
        {'id': genre_id, 'name': name, 'description': description},
    )
