from datetime import datetime, timedelta
from pathlib import Path
from typing import NamedTuple
from uuid import UUID

import pytest

from adapters.databases.in_memory.repositories.comments.comment import InMemCommentRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from config import settings
from deps.container import DIContainer
from domain.models import Comment, User
from domain.services.auth.types import CreateUserData
from tests.fixtures.game import Catalog


EARLIER_UUID = UUID('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d')
SAME_TIME_UUID = UUID('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e')
LATER_UUID = UUID('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f')
OTHER_GAME_UUID = UUID('d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f80')


class GameComments(NamedTuple):
    """Comments stored out of id order, plus their authors."""

    earlier: Comment
    same_time: Comment
    later: Comment
    other_game: Comment
    author: User
    other: User


@pytest.fixture
async def game_comments(
    di_container: DIContainer,
    registered_user: User,
    catalog: Catalog,
) -> GameComments:
    """Three comments on one game and one comment on another, with fixed times."""
    await di_container.auth_service().register_user(
        CreateUserData(email='other@mail.ru', password='secret', nickname='other'),
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None
    other = other.model_copy(update={'avatar_url': Path('avatars/other.png')})
    await InMemUserRepo().update(other)
    moment = datetime(2026, 10, 26, 12, tzinfo=settings.default_timezone)
    earlier = _comment(2, EARLIER_UUID, registered_user, catalog.disco.id, 'Earlier', moment)
    same_time = _comment(3, SAME_TIME_UUID, other, catalog.disco.id, 'Same time', moment)
    later = _comment(1, LATER_UUID, registered_user, catalog.disco.id, 'Later', moment + timedelta(hours=1))
    other_game = _comment(4, OTHER_GAME_UUID, registered_user, catalog.torment.id, 'Other game', moment)
    for comment in (later, earlier, same_time, other_game):
        await InMemCommentRepo().create(comment)
    return GameComments(
        earlier=earlier,
        same_time=same_time,
        later=later,
        other_game=other_game,
        author=registered_user,
        other=other,
    )


def _comment(
    comment_id: int,
    comment_uuid: UUID,
    user: User,
    game_id: int,
    text: str,
    created_at: datetime,
) -> Comment:
    return Comment(
        id=comment_id,
        uuid=comment_uuid,
        user_id=user.id,
        game_id=game_id,
        text=text,
        created_at=created_at,
        updated_at=created_at,
    )
