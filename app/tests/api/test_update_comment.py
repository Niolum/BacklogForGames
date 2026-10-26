from http import HTTPStatus
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient

from adapters.databases.in_memory.repositories.comments.comment import InMemCommentRepo
from domain.constants import COMMENT_TEXT_MAX_LENGTH
from entrypoints.fastapi.schemas.response import CommentResponseSchema
from tests.fixtures.game import Catalog


async def test_update_comment_requires_a_token(client: AsyncClient) -> None:
    """A request without a token is rejected."""
    response = await client.patch(f'/comments/{uuid4()}', json={'text': 'Edited'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


async def test_update_comment_returns_the_edited_comment(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """The author receives the comment with the new text and the same creation time."""
    headers = {'Authorization': f'Bearer {access_token}'}
    text = 'Edited'
    created = await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers=headers,
        json={'text': 'Worth replaying'},
    )
    response = await client.patch(
        f'/comments/{created.json()["uuid"]}',
        headers=headers,
        json={'text': text},
    )
    original = CommentResponseSchema.model_validate(created.json())
    comment = CommentResponseSchema.model_validate(response.json())

    assert created.status_code == HTTPStatus.CREATED
    assert response.status_code == HTTPStatus.OK
    assert comment.uuid == original.uuid
    assert comment.text == text
    assert comment.created_at == original.created_at
    assert comment.updated_at >= original.updated_at
    assert comment.author == original.author


@pytest.mark.parametrize(
    'text',
    ['', 'a' * (COMMENT_TEXT_MAX_LENGTH + 1)],
)
async def test_update_comment_rejects_text_outside_the_limit(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
    text: str,
) -> None:
    """Empty text and text longer than 1000 characters leave the comment unchanged."""
    headers = {'Authorization': f'Bearer {access_token}'}
    created = await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers=headers,
        json={'text': 'Worth replaying'},
    )
    response = await client.patch(
        f'/comments/{created.json()["uuid"]}',
        headers=headers,
        json={'text': text},
    )
    stored = await InMemCommentRepo().get_by_uuid(UUID(created.json()['uuid']))
    assert stored is not None
    original = CommentResponseSchema.model_validate(created.json())

    assert created.status_code == HTTPStatus.CREATED
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert stored.text == original.text
    assert stored.created_at == original.created_at
    assert stored.updated_at == original.updated_at


async def test_update_comment_unknown_comment_returns_404(client: AsyncClient, access_token: str) -> None:
    """An unknown comment returns 404."""
    missing_comment_uuid = UUID('00000000-0000-0000-0000-000000000099')

    response = await client.patch(
        f'/comments/{missing_comment_uuid}',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'text': 'Edited'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Comment with uuid={missing_comment_uuid} not found'}
    assert await InMemCommentRepo().get_by_uuid(missing_comment_uuid) is None


async def test_update_comment_rejects_another_users_comment(
    client: AsyncClient,
    access_token: str,
    other_access_token: str,
    catalog: Catalog,
) -> None:
    """Another user cannot change the comment, and the text stays."""
    created = await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'text': 'Worth replaying'},
    )
    comment_uuid = UUID(created.json()['uuid'])
    response = await client.patch(
        f'/comments/{comment_uuid}',
        headers={'Authorization': f'Bearer {other_access_token}'},
        json={'text': 'Edited'},
    )
    stored = await InMemCommentRepo().get_by_uuid(comment_uuid)
    assert stored is not None

    assert created.status_code == HTTPStatus.CREATED
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Comment with uuid={comment_uuid} not found'}
    assert stored.text == 'Worth replaying'
