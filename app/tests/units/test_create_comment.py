from uuid import UUID

import pytest

from adapters.databases.in_memory.repositories.comments.comment import InMemCommentRepo
from domain.exceptions import GameNotFoundError
from domain.models import User
from domain.services import AddUserGameData, CreateCommentData
from domain.use_cases import add_to_backlog, add_to_completed, create_comment
from tests.fixtures.game import Catalog


async def test_create_comment_stores_a_comment_for_a_published_game(registered_user: User, catalog: Catalog) -> None:
    """A published game gets a comment without a list row."""
    data = CreateCommentData(text='Worth replaying')

    item = await create_comment(registered_user, catalog.disco.uuid, data)
    stored = await InMemCommentRepo().get_by_uuid(item.uuid)

    assert stored is not None
    assert stored.uuid == item.uuid
    assert stored.user_id == registered_user.id
    assert stored.game_id == catalog.disco.id
    assert stored.text == data.text
    assert item.text == data.text
    assert item.created_at == stored.created_at
    assert item.updated_at == stored.updated_at
    assert item.author.uuid == registered_user.uuid
    assert item.author.nickname == registered_user.nickname
    assert item.author.avatar_url == registered_user.avatar_url


async def test_create_comment_ignores_list_status(registered_user: User, catalog: Catalog) -> None:
    """A backlog game, a completed game and a game outside the lists can all be commented."""
    await add_to_backlog(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.torment.uuid))
    text = CreateCommentData(text='Still thinking about it')

    backlog = await create_comment(registered_user, catalog.planescape.uuid, text)
    completed = await create_comment(registered_user, catalog.torment.uuid, text)
    absent = await create_comment(registered_user, catalog.disco.uuid, text)
    stored_game_ids = {comment.game_id for comment in InMemCommentRepo.DB.values()}

    assert backlog.uuid != completed.uuid
    assert completed.uuid != absent.uuid
    assert stored_game_ids == {catalog.planescape.id, catalog.torment.id, catalog.disco.id}


async def test_create_comment_rejects_an_unknown_game(registered_user: User) -> None:
    """An unknown game is not stored."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    with pytest.raises(GameNotFoundError, match=f'Game with uuid={missing_game_uuid} not found'):
        await create_comment(registered_user, missing_game_uuid, CreateCommentData(text='Hello'))

    assert InMemCommentRepo.DB == {}


async def test_create_comment_rejects_a_hidden_game(registered_user: User, catalog: Catalog) -> None:
    """A hidden game is not stored."""
    with pytest.raises(GameNotFoundError, match=f'Game with uuid={catalog.hidden.uuid} not found'):
        await create_comment(registered_user, catalog.hidden.uuid, CreateCommentData(text='Hello'))

    assert InMemCommentRepo.DB == {}
