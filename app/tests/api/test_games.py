from datetime import date
from http import HTTPStatus
from pathlib import Path
from typing import NamedTuple
from uuid import UUID

import pytest
from httpx import AsyncClient

from adapters.databases.in_memory.repositories.games.game import InMemGameRepo
from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from domain.models import Game, Genre


class Catalog(NamedTuple):
    """Published and hidden games saved with their genres."""

    planescape: Game
    torment: Game
    disco: Game
    hidden: Game
    rpg: Genre
    strategy: Genre


@pytest.fixture
async def catalog(
    game: Game,
    second_game: Game,
    third_game: Game,
    hidden_game: Game,
    genre: Genre,
    strategy_genre: Genre,
    clear_repositories: None,
) -> Catalog:
    """Save a small catalog: three published games and one hidden game."""
    del clear_repositories
    await InMemGenreRepo().create(genre)
    await InMemGenreRepo().create(strategy_genre)
    planescape = game.model_copy(
        update={
            'release_date': date(1999, 12, 6),
            'cover_url': Path('covers/planescape.png'),
            'description': 'A story',
            'metacritic': 91,
            'developer': 'Black Isle',
            'publisher': 'Interplay',
            'external_source': 'igdb',
            'external_id': '1',
            'genres': [genre, strategy_genre],
        },
    )
    torment = second_game.model_copy(update={'genres': [strategy_genre]})
    disco = third_game.model_copy(update={'genres': [genre]})
    hidden = hidden_game.model_copy(update={'genres': [genre], 'external_source': 'igdb', 'external_id': '2'})
    repo = InMemGameRepo()
    await repo.create(disco)
    await repo.create(planescape)
    await repo.create(torment)
    await repo.create(hidden)
    return Catalog(
        planescape=planescape,
        torment=torment,
        disco=disco,
        hidden=hidden,
        rpg=genre,
        strategy=strategy_genre,
    )


async def test_list_games_is_empty(client: AsyncClient) -> None:
    """The catalog is an empty page when no games are stored."""
    response = await client.get('/games')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'items': [], 'total': 0}


async def test_list_games_returns_published_games_without_token(client: AsyncClient, catalog: Catalog) -> None:
    """Anyone can read published games, ordered by title, without internal fields."""
    response = await client.get('/games')
    published = [
        {
            'uuid': str(catalog.disco.uuid),
            'title': catalog.disco.title,
            'release_date': None,
            'cover_url': None,
            'description': None,
            'metacritic': None,
            'developer': None,
            'publisher': None,
            'genres': [
                {'id': catalog.rpg.id, 'name': catalog.rpg.name, 'description': catalog.rpg.description},
            ],
        },
        {
            'uuid': str(catalog.planescape.uuid),
            'title': catalog.planescape.title,
            'release_date': '1999-12-06',
            'cover_url': 'covers/planescape.png',
            'description': 'A story',
            'metacritic': 91,
            'developer': 'Black Isle',
            'publisher': 'Interplay',
            'genres': [
                {'id': catalog.rpg.id, 'name': catalog.rpg.name, 'description': catalog.rpg.description},
                {
                    'id': catalog.strategy.id,
                    'name': catalog.strategy.name,
                    'description': catalog.strategy.description,
                },
            ],
        },
        {
            'uuid': str(catalog.torment.uuid),
            'title': catalog.torment.title,
            'release_date': None,
            'cover_url': None,
            'description': None,
            'metacritic': None,
            'developer': None,
            'publisher': None,
            'genres': [
                {
                    'id': catalog.strategy.id,
                    'name': catalog.strategy.name,
                    'description': catalog.strategy.description,
                },
            ],
        },
    ]

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'items': published, 'total': len(published)}


async def test_list_games_filters_by_genre_and_title(client: AsyncClient, catalog: Catalog) -> None:
    """genre_id and q keep published matches, and an unknown genre is an empty page."""
    matched = await client.get('/games', params={'genre_id': catalog.rpg.id, 'q': 'PLAN'})
    missing_genre = await client.get('/games', params={'genre_id': catalog.rpg.id + catalog.strategy.id})
    titles = [catalog.planescape.title]

    assert matched.status_code == HTTPStatus.OK
    assert [item['title'] for item in matched.json()['items']] == titles
    assert matched.json()['total'] == len(titles)
    assert missing_genre.status_code == HTTPStatus.OK
    assert missing_genre.json() == {'items': [], 'total': 0}


async def test_list_games_returns_the_requested_slice(client: AsyncClient, catalog: Catalog) -> None:
    """Offset and limit cut the page and leave the total unchanged."""
    response = await client.get('/games', params={'limit': 1, 'offset': 1})
    published = [catalog.disco, catalog.planescape, catalog.torment]

    assert response.status_code == HTTPStatus.OK
    assert [item['title'] for item in response.json()['items']] == [catalog.planescape.title]
    assert response.json()['total'] == len(published)


async def test_list_games_rejects_non_positive_limit(client: AsyncClient) -> None:
    """A limit below 1 is rejected before lookup."""
    response = await client.get('/games', params={'limit': 0, 'offset': -1})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_get_game_returns_published_card(client: AsyncClient, catalog: Catalog) -> None:
    """A known published uuid returns the card with genres and empty ratings."""
    response = await client.get(f'/games/{catalog.planescape.uuid}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'uuid': str(catalog.planescape.uuid),
        'title': catalog.planescape.title,
        'release_date': '1999-12-06',
        'cover_url': 'covers/planescape.png',
        'description': 'A story',
        'metacritic': 91,
        'developer': 'Black Isle',
        'publisher': 'Interplay',
        'genres': [
            {'id': catalog.rpg.id, 'name': catalog.rpg.name, 'description': catalog.rpg.description},
            {
                'id': catalog.strategy.id,
                'name': catalog.strategy.name,
                'description': catalog.strategy.description,
            },
        ],
        'users_score': None,
        'ratings_count': 0,
    }


async def test_get_game_unknown_uuid_returns_404(client: AsyncClient) -> None:
    """An unknown uuid returns 404."""
    missing_uuid = UUID('00000000-0000-0000-0000-000000000099')

    response = await client.get(f'/games/{missing_uuid}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={missing_uuid} not found'}


async def test_get_game_hidden_returns_404(client: AsyncClient, catalog: Catalog) -> None:
    """A hidden game is missing from the catalog."""
    response = await client.get(f'/games/{catalog.hidden.uuid}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={catalog.hidden.uuid} not found'}


async def test_get_game_rejects_non_uuid(client: AsyncClient) -> None:
    """A non-uuid path is rejected before lookup."""
    response = await client.get('/games/not-a-uuid')

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
