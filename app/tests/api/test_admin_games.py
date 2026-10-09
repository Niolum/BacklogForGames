from http import HTTPStatus
from pathlib import Path

from httpx import AsyncClient
from starlette.requests import Request

from adapters.databases.in_memory.repositories.games.game import InMemGameRepo
from domain.models import Game, Genre
from entrypoints.fastapi.admin.game import GameAdmin


async def test_admin_create_publishes_game_with_genres(
    admin_client: AsyncClient,
    stored_genre: Genre,
    stored_strategy_genre: Genre,
) -> None:
    """Saving the form stores a published game and shows it in the catalog."""
    metacritic = 91
    response = await admin_client.post(
        '/admin/game/create',
        data={
            'title': 'Planescape',
            'release_date': '1999-12-06',
            'description': 'A story',
            'metacritic': str(metacritic),
            'developer': 'Black Isle',
            'publisher': 'Interplay',
            'genres': [str(stored_genre.id), str(stored_strategy_genre.id)],
            'is_published': 'on',
            'save': 'Save',
        },
    )
    listed = await admin_client.get('/games')

    assert response.status_code == HTTPStatus.FOUND
    assert listed.status_code == HTTPStatus.OK
    assert listed.json()['total'] == 1
    item = listed.json()['items'][0]
    assert item['title'] == 'Planescape'
    assert item['release_date'] == '1999-12-06'
    assert item['description'] == 'A story'
    assert item['metacritic'] == metacritic
    assert item['developer'] == 'Black Isle'
    assert item['publisher'] == 'Interplay'
    assert [genre['name'] for genre in item['genres']] == ['RPG', 'Strategy']


async def test_admin_create_without_published_flag_hides_game(
    admin_client: AsyncClient,
    stored_genre: Genre,
) -> None:
    """An unchecked published flag keeps the game out of the catalog and the card."""
    response = await admin_client.post(
        '/admin/game/create',
        data={
            'title': 'Hidden Planescape',
            'genres': [str(stored_genre.id)],
            'save': 'Save',
        },
    )
    stored = next(iter(InMemGameRepo.DB.values()))
    catalog = await admin_client.get('/games')
    card = await admin_client.get(f'/games/{stored.uuid}')

    assert response.status_code == HTTPStatus.FOUND
    assert stored.is_published is False
    assert catalog.json() == {'items': [], 'total': 0}
    assert card.status_code == HTTPStatus.NOT_FOUND


async def test_admin_update_changes_fields_and_can_hide_game(
    client: AsyncClient,
    game: Game,
    stored_genre: Genre,
    stored_strategy_genre: Genre,
) -> None:
    """Edit changes the catalog fields, keeps the external identity, and can hide the game."""
    cover = Path('covers/planescape.png')
    await InMemGameRepo().create(
        game.model_copy(
            update={
                'cover_url': cover,
                'description': 'A story',
                'external_source': 'igdb',
                'external_id': '9',
                'genres': [stored_genre, stored_strategy_genre],
            },
        ),
    )

    metacritic = 85
    await GameAdmin().update_model(
        _request(),
        str(game.id),
        {
            'title': 'Torment',
            'release_date': '1998-11-30',
            'description': '',
            'metacritic': str(metacritic),
            'developer': 'Black Isle',
            'publisher': '',
            'is_published': False,
            'genres': [str(stored_strategy_genre.id)],
        },
    )
    stored = await InMemGameRepo().get_by_id(game.id)
    catalog = await client.get('/games')
    card = await client.get(f'/games/{game.uuid}')

    assert stored is not None
    assert stored.title == 'Torment'
    assert stored.release_date is not None
    assert stored.release_date.isoformat() == '1998-11-30'
    assert stored.description is None
    assert stored.metacritic == metacritic
    assert stored.developer == 'Black Isle'
    assert stored.publisher is None
    assert stored.is_published is False
    assert stored.cover_url == cover
    assert stored.external_source == 'igdb'
    assert stored.external_id == '9'
    assert [item.name for item in stored.genres] == ['Strategy']
    assert catalog.json() == {'items': [], 'total': 0}
    assert card.status_code == HTTPStatus.NOT_FOUND


def _request() -> Request:
    return Request({'type': 'http', 'method': 'POST', 'path': '/admin/game', 'headers': []})
