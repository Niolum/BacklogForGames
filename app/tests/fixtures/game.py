from datetime import UTC, datetime
from uuid import UUID

import pytest

from domain.models import Game


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
