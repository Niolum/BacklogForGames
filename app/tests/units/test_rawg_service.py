from http import HTTPMethod

import pytest

from adapters.http_fetchers import LocalHttpAPIFetcher
from config import rawg_settings
from deps.container import DIContainer


async def test_rawg_service_reads_one_games_page(di_container: DIContainer) -> None:
    """The list request asks for one page and does not follow the next link."""
    metacritic = 91
    page_size = 2
    genre_id = 5
    fetcher = _fetcher(di_container)
    fetcher.add_response(
        HTTPMethod.GET,
        'games',
        {
            'count': page_size,
            'next': 'https://api.rawg.io/api/games?page=2',
            'previous': None,
            'results': [
                {
                    'id': 1,
                    'name': 'Planescape',
                    'released': '1999-12-06',
                    'background_image': 'https://example.test/cover.jpg',
                    'metacritic': metacritic,
                    'genres': [{'id': genre_id, 'name': 'RPG', 'slug': 'rpg'}],
                },
                {
                    'id': 2,
                    'name': 'Hidden',
                    'released': None,
                    'background_image': None,
                    'metacritic': None,
                    'genres': [],
                },
            ],
        },
    )

    page = await di_container.rawg_service().get_games_page(page=1, page_size=page_size)

    assert len(fetcher.calls) == 1
    call = fetcher.calls[0]
    assert call.method is HTTPMethod.GET
    assert call.path == 'games'
    assert call.params is not None
    assert call.params['key'] == rawg_settings.api_key.get_secret_value()
    assert call.params['page'] == 1
    assert call.params['page_size'] == page_size
    assert page.count == page_size
    assert page.next == 'https://api.rawg.io/api/games?page=2'
    first = page.results[0]
    assert first.name == 'Planescape'
    assert first.released is not None
    assert first.released.isoformat() == '1999-12-06'
    assert first.background_image == 'https://example.test/cover.jpg'
    assert first.metacritic == metacritic
    assert [genre.id for genre in first.genres] == [genre_id]
    second = page.results[1]
    assert second.released is None
    assert second.background_image is None
    assert second.metacritic is None
    assert second.genres == []


async def test_rawg_service_reads_one_game_card(di_container: DIContainer) -> None:
    """The game card request reads description, developers and publishers."""
    fetcher = _fetcher(di_container)
    fetcher.add_response(
        HTTPMethod.GET,
        'games/1',
        {
            'id': 1,
            'description': 'A story',
            'developers': [{'id': 3, 'name': 'Black Isle', 'slug': 'black-isle'}],
            'publishers': [{'id': 4, 'name': 'Interplay'}],
        },
    )

    card = await di_container.rawg_service().get_game(1)

    assert len(fetcher.calls) == 1
    call = fetcher.calls[0]
    assert call.path == 'games/1'
    assert call.params is not None
    assert call.params['key'] == rawg_settings.api_key.get_secret_value()
    assert card.description == 'A story'
    assert [company.name for company in card.developers] == ['Black Isle']
    assert [company.name for company in card.publishers] == ['Interplay']


async def test_rawg_service_reads_one_genre_card(di_container: DIContainer) -> None:
    """The genre card request reads the name and description."""
    genre_id = 5
    fetcher = _fetcher(di_container)
    fetcher.add_response(
        HTTPMethod.GET,
        f'genres/{genre_id}',
        {'id': genre_id, 'name': 'RPG', 'slug': 'rpg', 'description': 'Role-playing'},
    )

    card = await di_container.rawg_service().get_genre(genre_id)

    assert len(fetcher.calls) == 1
    assert fetcher.calls[0].path == f'genres/{genre_id}'
    assert card.id == genre_id
    assert card.name == 'RPG'
    assert card.description == 'Role-playing'


def _fetcher(di_container: DIContainer) -> LocalHttpAPIFetcher:
    """Return the local fetcher selected for tests."""
    fetcher = di_container.http_fetcher()
    if not isinstance(fetcher, LocalHttpAPIFetcher):
        msg = 'Tests use the local HTTP fetcher'
        raise TypeError(msg)
    return fetcher


async def test_local_http_fetcher_rejects_unknown_path() -> None:
    """A path without a prepared response is an error."""
    fetcher = LocalHttpAPIFetcher()

    with pytest.raises(LookupError, match='No local response for GET games'):
        await fetcher.make_request(HTTPMethod.GET, 'games')
