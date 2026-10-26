from uuid import UUID

import pytest

from domain.constants import DEFAULT_LIMIT
from domain.exceptions import GameNotFoundError
from domain.use_cases import get_game_comments
from tests.fixtures.comment import GameComments
from tests.fixtures.game import Catalog


async def test_get_game_comments_returns_an_empty_page(catalog: Catalog) -> None:
    """A published game without comments has an empty page."""
    page = await get_game_comments(catalog.disco.uuid, limit=DEFAULT_LIMIT, offset=0)

    assert page.items == []
    assert page.total == len(page.items)


async def test_get_game_comments_orders_by_creation_time_then_id(
    catalog: Catalog,
    game_comments: GameComments,
) -> None:
    """Comments are ordered by creation time, then id, and carry the author."""
    disco_comments = [game_comments.earlier, game_comments.same_time, game_comments.later]

    page = await get_game_comments(catalog.disco.uuid, limit=len(disco_comments), offset=0)
    first, second, third = page.items

    assert page.total == len(disco_comments)
    assert [item.uuid for item in page.items] == [comment.uuid for comment in disco_comments]
    assert first.text == game_comments.earlier.text
    assert first.created_at == game_comments.earlier.created_at
    assert first.updated_at == game_comments.earlier.updated_at
    assert first.author.uuid == game_comments.author.uuid
    assert first.author.nickname == game_comments.author.nickname
    assert first.author.avatar_url == game_comments.author.avatar_url
    assert second.author.uuid == game_comments.other.uuid
    assert second.author.nickname == game_comments.other.nickname
    assert second.author.avatar_url == game_comments.other.avatar_url
    assert third.uuid == game_comments.later.uuid
    assert game_comments.other_game.uuid not in {item.uuid for item in page.items}


async def test_get_game_comments_returns_the_requested_slice(catalog: Catalog, game_comments: GameComments) -> None:
    """Offset and limit cut the page and leave the total unchanged."""
    disco_comments = [game_comments.earlier, game_comments.same_time, game_comments.later]

    page = await get_game_comments(catalog.disco.uuid, limit=1, offset=1)

    assert [item.uuid for item in page.items] == [game_comments.same_time.uuid]
    assert page.total == len(disco_comments)


async def test_get_game_comments_rejects_an_unknown_game() -> None:
    """An unknown game is not listed."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    with pytest.raises(GameNotFoundError, match=f'Game with uuid={missing_game_uuid} not found'):
        await get_game_comments(missing_game_uuid, limit=DEFAULT_LIMIT, offset=0)


async def test_get_game_comments_rejects_a_hidden_game(catalog: Catalog) -> None:
    """A hidden game is not listed."""
    with pytest.raises(GameNotFoundError, match=f'Game with uuid={catalog.hidden.uuid} not found'):
        await get_game_comments(catalog.hidden.uuid, limit=DEFAULT_LIMIT, offset=0)
