from datetime import datetime
from uuid import UUID

import pytest

from adapters.databases.in_memory.repositories.comments.comment import InMemCommentRepo
from config import settings
from domain.exceptions import CommentNotFoundError
from domain.services import UpdateCommentData
from domain.use_cases import update_comment
from tests.fixtures.comment import GameComments


async def test_update_comment_replaces_text_and_update_time(game_comments: GameComments) -> None:
    """The author saves new text and a new update time. The creation time stays."""
    data = UpdateCommentData(text='Edited')
    before = datetime.now(settings.default_timezone)

    item = await update_comment(game_comments.author, game_comments.earlier.uuid, data)
    stored = await InMemCommentRepo().get_by_uuid(item.uuid)
    untouched = await InMemCommentRepo().get_by_uuid(game_comments.later.uuid)

    assert stored is not None
    assert untouched is not None
    assert stored.text == data.text
    assert item.text == data.text
    assert stored.created_at == game_comments.earlier.created_at
    assert item.created_at == game_comments.earlier.created_at
    assert stored.updated_at >= before
    assert item.updated_at == stored.updated_at
    assert item.author.uuid == game_comments.author.uuid
    assert item.author.nickname == game_comments.author.nickname
    assert item.author.avatar_url == game_comments.author.avatar_url
    assert untouched.text == game_comments.later.text
    assert untouched.updated_at == game_comments.later.updated_at


async def test_update_comment_rejects_another_users_comment(game_comments: GameComments) -> None:
    """Another user's comment stays unchanged."""
    comment_uuid = game_comments.same_time.uuid

    with pytest.raises(CommentNotFoundError, match=f'Comment with uuid={comment_uuid} not found'):
        await update_comment(game_comments.author, comment_uuid, UpdateCommentData(text='Edited'))

    stored = await InMemCommentRepo().get_by_uuid(comment_uuid)
    assert stored is not None
    assert stored.text == game_comments.same_time.text
    assert stored.updated_at == game_comments.same_time.updated_at


async def test_update_comment_rejects_an_unknown_comment(game_comments: GameComments) -> None:
    """An unknown comment is not stored."""
    missing_comment_uuid = UUID('00000000-0000-0000-0000-000000000099')

    with pytest.raises(CommentNotFoundError, match=f'Comment with uuid={missing_comment_uuid} not found'):
        await update_comment(game_comments.author, missing_comment_uuid, UpdateCommentData(text='Edited'))

    assert await InMemCommentRepo().get_by_uuid(missing_comment_uuid) is None
    stored = await InMemCommentRepo().get_by_uuid(game_comments.earlier.uuid)
    assert stored is not None
    assert stored.text == game_comments.earlier.text
