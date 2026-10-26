from http import HTTPStatus
from typing import TypedDict
from uuid import UUID

import pytest
from httpx import AsyncClient

from adapters.databases.in_memory.repositories.comments.comment import InMemCommentRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from entrypoints.fastapi.schemas.response import CommentResponseSchema
from tests.fixtures.game import Catalog


class _ExpectedAuthor(TypedDict):
    nickname: str
    avatar_url: None


class _ExpectedComment(TypedDict):
    text: str
    author: _ExpectedAuthor


async def test_create_comment_requires_a_token(client: AsyncClient, catalog: Catalog) -> None:
    """A request without a token is rejected."""
    response = await client.post(f'/games/{catalog.disco.uuid}/comments', json={'text': 'Hello'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}
    assert InMemCommentRepo.DB == {}


@pytest.mark.parametrize(
    'expected',
    [
        {
            'text': 'Worth replaying',
            'author': {
                'nickname': 'nick',
                'avatar_url': None,
            },
        },
    ],
)
async def test_create_comment_returns_the_created_comment(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
    expected: _ExpectedComment,
) -> None:
    """The current user comments on a published game and receives that comment."""
    response = await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'text': expected['text']},
    )
    author = await InMemUserRepo().get_by_email('user@mail.ru')
    assert author is not None
    body = response.json()
    stored = await InMemCommentRepo().get_by_uuid(UUID(body['uuid']))
    assert stored is not None
    comment = CommentResponseSchema.model_validate(body)

    assert response.status_code == HTTPStatus.CREATED
    assert comment.text == expected['text']
    assert comment.author.nickname == expected['author']['nickname']
    assert comment.author.avatar_url == expected['author']['avatar_url']
    assert comment.uuid == stored.uuid
    assert comment.author.uuid == author.uuid
    assert comment.created_at == stored.created_at
    assert comment.updated_at == stored.updated_at
    assert stored.user_id == author.id
    assert stored.game_id == catalog.disco.id


async def test_create_comment_unknown_game_returns_404(client: AsyncClient, access_token: str) -> None:
    """An unknown game returns 404."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    response = await client.post(
        f'/games/{missing_game_uuid}/comments',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'text': 'Hello'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={missing_game_uuid} not found'}
    assert InMemCommentRepo.DB == {}


async def test_create_comment_hidden_game_returns_404(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """A hidden game returns 404."""
    response = await client.post(
        f'/games/{catalog.hidden.uuid}/comments',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'text': 'Hello'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={catalog.hidden.uuid} not found'}
    assert InMemCommentRepo.DB == {}
