from datetime import UTC, date, datetime
from pathlib import Path
from typing import NamedTuple
from uuid import UUID

import pytest

from adapters.databases.in_memory.repositories.games.game import InMemGameRepo
from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from domain.models import Game, Genre


GAME_UUID = UUID('6f1d8c2a-4b7e-4d1a-9c3f-2a8b6e5d4c31')
SECOND_GAME_UUID = UUID('7a2e9d3b-5c8f-4e2b-8d4a-3b9c7f6e5d42')
THIRD_GAME_UUID = UUID('8b3f0e4c-6d9a-4f3c-9e5b-4c0d8a7f6e53')
HIDDEN_GAME_UUID = UUID('9c4a1f5d-7e0b-4a4d-0f6c-5d1e9b8a7f64')


def _game(
    game_id: int,
    game_uuid: UUID,
    title: str,
    *,
    is_published: bool = True,
) -> Game:
    moment = datetime(2026, 10, 9, tzinfo=UTC)
    return Game(
        id=game_id,
        uuid=game_uuid,
        title=title,
        is_published=is_published,
        created_at=moment,
        updated_at=moment,
    )


@pytest.fixture
def game() -> Game:
    """Published game used as the stored record in repository tests."""
    return _game(1, GAME_UUID, 'Planescape')


@pytest.fixture
def second_game() -> Game:
    """Second published game with a higher id."""
    return _game(2, SECOND_GAME_UUID, 'Torment')


@pytest.fixture
def third_game() -> Game:
    """Third published game with the highest id."""
    return _game(3, THIRD_GAME_UUID, 'Disco Elysium')


@pytest.fixture
def hidden_game() -> Game:
    """Unpublished game."""
    return _game(4, HIDDEN_GAME_UUID, 'Hidden Planescape', is_published=False)


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
