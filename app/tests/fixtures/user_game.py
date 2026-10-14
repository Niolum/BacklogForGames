from datetime import UTC, datetime

import pytest

from adapters.databases.in_memory.repositories.user_games.user_game import InMemUserGameRepo
from domain.models import User, UserGame, UserGameStatus
from tests.fixtures.game import Catalog


@pytest.fixture
async def listed_user(registered_user: User, catalog: Catalog) -> User:
    """User with a backlog, one completed game, and another user's row."""
    created_at = datetime(2026, 10, 14, tzinfo=UTC)
    completed_at = datetime(2026, 10, 14, 15, tzinfo=UTC)
    other_user_id = registered_user.id + 1
    repo = InMemUserGameRepo()
    await repo.create(
        UserGame(
            id=1,
            user_id=registered_user.id,
            game_id=catalog.planescape.id,
            status=UserGameStatus.backlog,
            created_at=created_at,
        ),
    )
    await repo.create(
        UserGame(
            id=2,
            user_id=registered_user.id,
            game_id=catalog.torment.id,
            status=UserGameStatus.completed,
            created_at=created_at,
            completed_at=completed_at,
        ),
    )
    await repo.create(
        UserGame(
            id=3,
            user_id=registered_user.id,
            game_id=catalog.disco.id,
            status=UserGameStatus.backlog,
            created_at=created_at,
        ),
    )
    await repo.create(
        UserGame(
            id=4,
            user_id=other_user_id,
            game_id=catalog.planescape.id,
            status=UserGameStatus.backlog,
            created_at=created_at,
        ),
    )
    return registered_user
