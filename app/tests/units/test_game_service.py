from datetime import date
from pathlib import Path

import pytest

from adapters.databases.in_memory.repositories.games.game import InMemGameRepo
from deps.container import DIContainer
from domain.exceptions import GameNotFoundError, GenreNotFoundError
from domain.models import Game, Genre
from domain.services import GameChangeData, GameCreateData


async def test_create_game_stores_fields_and_genres(
    di_container: DIContainer,
    stored_genre: Genre,
    stored_strategy_genre: Genre,
) -> None:
    """A new game keeps its genres and turns empty text into no text."""
    release_date = date(1999, 12, 6)
    metacritic = 91
    game = await di_container.game_service().create_game(
        GameCreateData(
            title='Planescape',
            release_date=release_date,
            description='',
            metacritic=metacritic,
            developer='Black Isle',
            publisher='',
            genres=[stored_strategy_genre.id, stored_genre.id, stored_genre.id],
        ),
    )

    stored = await InMemGameRepo().get_by_id(game.id)
    assert stored is not None
    assert stored.title == 'Planescape'
    assert stored.release_date == release_date
    assert stored.description is None
    assert stored.metacritic == metacritic
    assert stored.developer == 'Black Isle'
    assert stored.publisher is None
    assert stored.is_published is True
    assert stored.cover_url is None
    assert stored.external_source is None
    assert stored.external_id is None
    assert [item.name for item in stored.genres] == ['RPG', 'Strategy']


async def test_create_game_rejects_empty_title(di_container: DIContainer) -> None:
    """An empty title is not saved."""
    with pytest.raises(ValueError, match='Game title is empty'):
        await di_container.game_service().create_game(GameCreateData(title=''))

    assert list(InMemGameRepo.DB) == []


async def test_create_game_rejects_unknown_genre(di_container: DIContainer) -> None:
    """A missing genre is not stored with the game."""
    missing_id = 9
    with pytest.raises(GenreNotFoundError, match=f'Genre with id={missing_id} not found'):
        await di_container.game_service().create_game(GameCreateData(title='Planescape', genres=[missing_id]))

    assert list(InMemGameRepo.DB) == []


async def test_update_game_keeps_external_fields_and_cover(
    di_container: DIContainer,
    game: Game,
    stored_genre: Genre,
    stored_strategy_genre: Genre,
) -> None:
    """Edit replaces the published fields and leaves the external identity and cover."""
    cover = Path('covers/planescape.png')
    await InMemGameRepo().create(
        game.model_copy(
            update={
                'cover_url': cover,
                'external_source': 'igdb',
                'external_id': '9',
                'genres': [stored_genre],
            },
        ),
    )
    metacritic = 85
    release_date = date(1998, 11, 30)

    updated = await di_container.game_service().update_game(
        game.id,
        GameChangeData(
            title='Torment',
            release_date=release_date,
            description='',
            metacritic=metacritic,
            developer='Black Isle',
            publisher='',
            is_published=False,
            genres=[stored_strategy_genre.id],
        ),
    )

    stored = await InMemGameRepo().get_by_id(game.id)
    assert stored is not None
    assert stored == updated
    assert stored.title == 'Torment'
    assert stored.release_date == release_date
    assert stored.description is None
    assert stored.metacritic == metacritic
    assert stored.publisher is None
    assert stored.is_published is False
    assert stored.cover_url == cover
    assert stored.external_source == 'igdb'
    assert stored.external_id == '9'
    assert stored.uuid == game.uuid
    assert [item.name for item in stored.genres] == ['Strategy']
    assert stored.updated_at != game.updated_at


async def test_update_game_rejects_unknown_id(di_container: DIContainer, game: Game) -> None:
    """An unknown id raises not found."""
    with pytest.raises(GameNotFoundError, match=f'Game with id={game.id} not found'):
        await di_container.game_service().update_game(game.id, GameChangeData(title='Torment'))
