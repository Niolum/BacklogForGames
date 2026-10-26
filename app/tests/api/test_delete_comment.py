from http import HTTPStatus
from uuid import UUID, uuid4

from httpx import AsyncClient

from adapters.databases.in_memory.repositories.comments.comment import InMemCommentRepo
from tests.fixtures.game import Catalog


async def test_delete_comment_requires_a_token(client: AsyncClient) -> None:
    """A request without a token is rejected."""
    response = await client.delete(f'/comments/{uuid4()}')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


async def test_delete_comment_removes_the_authors_comment(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """The author removes one comment and receives an empty body. The other comment stays."""
    headers = {'Authorization': f'Bearer {access_token}'}
    first = await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers=headers,
        json={'text': 'First'},
    )
    second = await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers=headers,
        json={'text': 'Second'},
    )
    removed = UUID(first.json()['uuid'])
    response = await client.delete(f'/comments/{removed}', headers=headers)
    page = await client.get(f'/games/{catalog.disco.uuid}/comments')
    kept = [second.json()]

    assert first.status_code == HTTPStatus.CREATED
    assert second.status_code == HTTPStatus.CREATED
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''
    assert await InMemCommentRepo().get_by_uuid(removed) is None
    assert page.json() == {'items': kept, 'total': len(kept)}


async def test_delete_comment_unknown_comment_returns_404(client: AsyncClient, access_token: str) -> None:
    """An unknown comment returns 404."""
    missing_comment_uuid = UUID('00000000-0000-0000-0000-000000000099')

    response = await client.delete(
        f'/comments/{missing_comment_uuid}',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Comment with uuid={missing_comment_uuid} not found'}


async def test_delete_comment_rejects_another_users_comment(
    client: AsyncClient,
    access_token: str,
    other_access_token: str,
    catalog: Catalog,
) -> None:
    """Another user cannot remove the comment, and the row stays."""
    created = await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'text': 'Worth replaying'},
    )
    comment_uuid = UUID(created.json()['uuid'])
    response = await client.delete(
        f'/comments/{comment_uuid}',
        headers={'Authorization': f'Bearer {other_access_token}'},
    )
    stored = await InMemCommentRepo().get_by_uuid(comment_uuid)

    assert created.status_code == HTTPStatus.CREATED
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Comment with uuid={comment_uuid} not found'}
    assert stored is not None
    assert stored.text == 'Worth replaying'
