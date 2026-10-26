import os
import shutil
from pathlib import Path

import pytest

from adapters.databases.in_memory.repositories.comments.comment import InMemCommentRepo
from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import (
    InMemEmailConfirmationRepo,
)
from adapters.databases.in_memory.repositories.games.game import InMemGameRepo
from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from adapters.databases.in_memory.repositories.ratings.rating import InMemRatingRepo
from adapters.databases.in_memory.repositories.user_games.user_game import InMemUserGameRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo


@pytest.fixture(autouse=True)
def clear_repositories() -> None:
    """Drop records and local files left by a previous test."""
    InMemUserRepo.DB.clear()
    InMemEmailConfirmationRepo.DB.clear()
    InMemGenreRepo.DB.clear()
    InMemGameRepo.DB.clear()
    InMemUserGameRepo.DB.clear()
    InMemRatingRepo.DB.clear()
    InMemCommentRepo.DB.clear()
    root = Path(os.environ['STORAGE_CONFIG__LOCAL_ROOT'])
    if root.exists():
        shutil.rmtree(root)
    root.mkdir()
