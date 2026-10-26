from uuid import UUID

import pytest

from adapters.databases.in_memory.repositories.comments.comment import InMemCommentRepo
from domain.exceptions import CommentNotFoundError
from domain.use_cases import delete_comment
from tests.fixtures.comment import GameComments


async def test_delete_comment_removes_the_authors_comment(game_comments: GameComments) -> None:
    """The author removes one comment. The other comments stay."""
    await delete_comment(game_comments.author, game_comments.earlier.uuid)

    assert await InMemCommentRepo().get_by_uuid(game_comments.earlier.uuid) is None
    kept = await InMemCommentRepo().get_by_uuid(game_comments.later.uuid)
    assert kept is not None
    assert kept.text == game_comments.later.text
    other = await InMemCommentRepo().get_by_uuid(game_comments.same_time.uuid)
    assert other is not None
    assert other.text == game_comments.same_time.text


async def test_delete_comment_rejects_another_users_comment(game_comments: GameComments) -> None:
    """Another user's comment stays."""
    comment_uuid = game_comments.same_time.uuid

    with pytest.raises(CommentNotFoundError, match=f'Comment with uuid={comment_uuid} not found'):
        await delete_comment(game_comments.author, comment_uuid)

    stored = await InMemCommentRepo().get_by_uuid(comment_uuid)
    assert stored is not None
    assert stored.text == game_comments.same_time.text


async def test_delete_comment_rejects_an_unknown_comment(game_comments: GameComments) -> None:
    """An unknown comment leaves the stored rows in place."""
    missing_comment_uuid = UUID('00000000-0000-0000-0000-000000000099')

    with pytest.raises(CommentNotFoundError, match=f'Comment with uuid={missing_comment_uuid} not found'):
        await delete_comment(game_comments.author, missing_comment_uuid)

    stored = await InMemCommentRepo().get_by_uuid(game_comments.earlier.uuid)
    assert stored is not None
    assert stored.text == game_comments.earlier.text
