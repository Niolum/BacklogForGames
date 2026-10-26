from http import HTTPStatus
from uuid import uuid4

from httpx import AsyncClient

from domain.models import User
from tests.fixtures.game import Catalog


async def test_user_lists_are_empty_without_token(client: AsyncClient, registered_user: User) -> None:
    """A user with no rows has empty backlog and completed pages, and no token is sent."""
    backlog = await client.get(f'/users/{registered_user.uuid}/backlog')
    completed = await client.get(f'/users/{registered_user.uuid}/completed')

    assert backlog.status_code == HTTPStatus.OK
    assert backlog.json() == {'items': [], 'total': 0}
    assert completed.status_code == HTTPStatus.OK
    assert completed.json() == {'items': [], 'total': 0}


async def test_user_lists_return_cover_title_and_genres(
    client: AsyncClient,
    listed_user: User,
    catalog: Catalog,
) -> None:
    """Each list returns that user's games, ordered by title, with uuid, cover and genres."""
    backlog = await client.get(f'/users/{listed_user.uuid}/backlog')
    completed = await client.get(f'/users/{listed_user.uuid}/completed')
    backlog_items = [
        {
            'uuid': str(catalog.disco.uuid),
            'cover_url': None,
            'title': catalog.disco.title,
            'genres': [
                {'id': catalog.rpg.id, 'name': catalog.rpg.name, 'description': catalog.rpg.description},
            ],
        },
        {
            'uuid': str(catalog.planescape.uuid),
            'cover_url': 'covers/planescape.png',
            'title': catalog.planescape.title,
            'genres': [
                {'id': catalog.rpg.id, 'name': catalog.rpg.name, 'description': catalog.rpg.description},
                {
                    'id': catalog.strategy.id,
                    'name': catalog.strategy.name,
                    'description': catalog.strategy.description,
                },
            ],
        },
    ]
    completed_items = [
        {
            'uuid': str(catalog.torment.uuid),
            'cover_url': None,
            'title': catalog.torment.title,
            'genres': [
                {
                    'id': catalog.strategy.id,
                    'name': catalog.strategy.name,
                    'description': catalog.strategy.description,
                },
            ],
            'user_score': None,
        },
    ]

    assert backlog.status_code == HTTPStatus.OK
    assert backlog.json() == {'items': backlog_items, 'total': len(backlog_items)}
    assert completed.status_code == HTTPStatus.OK
    assert completed.json() == {'items': completed_items, 'total': len(completed_items)}


async def test_user_lists_return_the_requested_slice(client: AsyncClient, listed_user: User, catalog: Catalog) -> None:
    """Offset and limit cut the backlog and leave the total unchanged."""
    response = await client.get(f'/users/{listed_user.uuid}/backlog', params={'limit': 1, 'offset': 1})
    backlog_titles = [catalog.disco.title, catalog.planescape.title]

    assert response.status_code == HTTPStatus.OK
    assert [item['title'] for item in response.json()['items']] == [catalog.planescape.title]
    assert response.json()['total'] == len(backlog_titles)


async def test_user_lists_missing_user_returns_404(client: AsyncClient) -> None:
    """An unknown user uuid returns 404 for both lists."""
    missing = uuid4()

    backlog = await client.get(f'/users/{missing}/backlog')
    completed = await client.get(f'/users/{missing}/completed')

    assert backlog.status_code == HTTPStatus.NOT_FOUND
    assert backlog.json() == {'detail': f'User with uuid={missing} not found'}
    assert completed.status_code == HTTPStatus.NOT_FOUND
    assert completed.json() == {'detail': f'User with uuid={missing} not found'}


async def test_user_lists_reject_non_positive_limit(client: AsyncClient, registered_user: User) -> None:
    """A limit below 1 or a negative offset is rejected before lookup."""
    response = await client.get(f'/users/{registered_user.uuid}/backlog', params={'limit': 0, 'offset': -1})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_user_lists_reject_non_uuid(client: AsyncClient) -> None:
    """A non-uuid path is rejected before lookup."""
    response = await client.get('/users/not-a-uuid/backlog')

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_completed_list_returns_the_owners_score(
    client: AsyncClient,
    access_token: str,
    other_access_token: str,
    catalog: Catalog,
) -> None:
    """The completed list shows the owner's score without a token. The backlog omits that field."""
    owner_score = 7
    hidden_score = 4
    other_score = 9
    owner_headers = {'Authorization': f'Bearer {access_token}'}
    other_headers = {'Authorization': f'Bearer {other_access_token}'}
    owner = await client.get('/users/me', headers=owner_headers)
    stranger = await client.get('/users/me', headers=other_headers)
    disco = await client.post(
        '/users/me/completed',
        headers=owner_headers,
        json={'game_uuid': str(catalog.disco.uuid)},
    )
    planescape = await client.post(
        '/users/me/completed',
        headers=owner_headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    rated = await client.put(
        f'/games/{catalog.planescape.uuid}/rating',
        headers=owner_headers,
        json={'score': owner_score},
    )
    hidden = await client.post(
        '/users/me/completed',
        headers=owner_headers,
        json={'game_uuid': str(catalog.hidden.uuid)},
    )
    hidden_rated = await client.put(
        f'/games/{catalog.hidden.uuid}/rating',
        headers=owner_headers,
        json={'score': hidden_score},
    )
    backlog_row = await client.post(
        '/users/me/backlog',
        headers=owner_headers,
        json={'game_uuid': str(catalog.torment.uuid)},
    )
    other_completed = await client.post(
        '/users/me/completed',
        headers=other_headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    other_rated = await client.put(
        f'/games/{catalog.planescape.uuid}/rating',
        headers=other_headers,
        json={'score': other_score},
    )
    completed = await client.get(f'/users/{owner.json()["uuid"]}/completed')
    backlog = await client.get(f'/users/{owner.json()["uuid"]}/backlog')
    stranger_completed = await client.get(f'/users/{stranger.json()["uuid"]}/completed')

    assert owner.status_code == HTTPStatus.OK
    assert stranger.status_code == HTTPStatus.OK
    assert disco.status_code == HTTPStatus.CREATED
    assert planescape.status_code == HTTPStatus.CREATED
    assert rated.status_code == HTTPStatus.OK
    assert hidden.status_code == HTTPStatus.CREATED
    assert hidden_rated.status_code == HTTPStatus.OK
    assert backlog_row.status_code == HTTPStatus.CREATED
    assert other_completed.status_code == HTTPStatus.CREATED
    assert other_rated.status_code == HTTPStatus.OK
    assert completed.status_code == HTTPStatus.OK
    assert [item['title'] for item in completed.json()['items']] == [
        catalog.disco.title,
        catalog.hidden.title,
        catalog.planescape.title,
    ]
    assert [item['user_score'] for item in completed.json()['items']] == [None, hidden_score, owner_score]
    assert completed.json()['total'] == len([catalog.disco, catalog.hidden, catalog.planescape])
    assert backlog.status_code == HTTPStatus.OK
    assert [item['title'] for item in backlog.json()['items']] == [catalog.torment.title]
    assert all('user_score' not in item for item in backlog.json()['items'])
    assert stranger_completed.status_code == HTTPStatus.OK
    assert [item['user_score'] for item in stranger_completed.json()['items']] == [other_score]
