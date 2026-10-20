from http import HTTPStatus
from uuid import UUID

from httpx import AsyncClient

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import InMemEmailConfirmationRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from tests.fixtures.game import Catalog


async def test_list_games_is_empty(client: AsyncClient) -> None:
    """The catalog is an empty page when no games are stored."""
    response = await client.get('/games')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'items': [], 'total': 0}


async def test_list_games_returns_published_games_without_token(client: AsyncClient, catalog: Catalog) -> None:
    """Anyone can read published games, ordered by title, without internal fields."""
    response = await client.get('/games')
    published = [
        {
            'uuid': str(catalog.disco.uuid),
            'title': catalog.disco.title,
            'release_date': None,
            'cover_url': None,
            'description': None,
            'metacritic': None,
            'developer': None,
            'publisher': None,
            'genres': [
                {'id': catalog.rpg.id, 'name': catalog.rpg.name, 'description': catalog.rpg.description},
            ],
        },
        {
            'uuid': str(catalog.planescape.uuid),
            'title': catalog.planescape.title,
            'release_date': '1999-12-06',
            'cover_url': 'covers/planescape.png',
            'description': 'A story',
            'metacritic': 91,
            'developer': 'Black Isle',
            'publisher': 'Interplay',
            'genres': [
                {'id': catalog.rpg.id, 'name': catalog.rpg.name, 'description': catalog.rpg.description},
                {
                    'id': catalog.strategy.id,
                    'name': catalog.strategy.name,
                    'description': catalog.strategy.description,
                },
            ],
        },
        {
            'uuid': str(catalog.torment.uuid),
            'title': catalog.torment.title,
            'release_date': None,
            'cover_url': None,
            'description': None,
            'metacritic': None,
            'developer': None,
            'publisher': None,
            'genres': [
                {
                    'id': catalog.strategy.id,
                    'name': catalog.strategy.name,
                    'description': catalog.strategy.description,
                },
            ],
        },
    ]

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'items': published, 'total': len(published)}


async def test_list_games_filters_by_genre_and_title(client: AsyncClient, catalog: Catalog) -> None:
    """genre_id and q keep published matches, and an unknown genre is an empty page."""
    matched = await client.get('/games', params={'genre_id': catalog.rpg.id, 'q': 'PLAN'})
    missing_genre = await client.get('/games', params={'genre_id': catalog.rpg.id + catalog.strategy.id})
    titles = [catalog.planescape.title]

    assert matched.status_code == HTTPStatus.OK
    assert [item['title'] for item in matched.json()['items']] == titles
    assert matched.json()['total'] == len(titles)
    assert missing_genre.status_code == HTTPStatus.OK
    assert missing_genre.json() == {'items': [], 'total': 0}


async def test_list_games_returns_the_requested_slice(client: AsyncClient, catalog: Catalog) -> None:
    """Offset and limit cut the page and leave the total unchanged."""
    response = await client.get('/games', params={'limit': 1, 'offset': 1})
    published = [catalog.disco, catalog.planescape, catalog.torment]

    assert response.status_code == HTTPStatus.OK
    assert [item['title'] for item in response.json()['items']] == [catalog.planescape.title]
    assert response.json()['total'] == len(published)


async def test_list_games_rejects_non_positive_limit(client: AsyncClient) -> None:
    """A limit below 1 is rejected before lookup."""
    response = await client.get('/games', params={'limit': 0, 'offset': -1})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_get_game_returns_published_card(client: AsyncClient, catalog: Catalog) -> None:
    """A known published uuid returns the card with genres and empty ratings."""
    response = await client.get(f'/games/{catalog.planescape.uuid}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'uuid': str(catalog.planescape.uuid),
        'title': catalog.planescape.title,
        'release_date': '1999-12-06',
        'cover_url': 'covers/planescape.png',
        'description': 'A story',
        'metacritic': 91,
        'developer': 'Black Isle',
        'publisher': 'Interplay',
        'genres': [
            {'id': catalog.rpg.id, 'name': catalog.rpg.name, 'description': catalog.rpg.description},
            {
                'id': catalog.strategy.id,
                'name': catalog.strategy.name,
                'description': catalog.strategy.description,
            },
        ],
        'users_score': None,
        'ratings_count': 0,
        'user_score': None,
    }


async def test_get_game_returns_the_average_of_several_scores(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """The game card returns the average rating and the number of ratings."""
    scores = [8, 9]
    owner_headers = {'Authorization': f'Bearer {access_token}'}
    completed = await client.post(
        '/users/me/completed',
        headers=owner_headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    first = await client.put(
        f'/games/{catalog.planescape.uuid}/rating',
        headers=owner_headers,
        json={'score': scores[0]},
    )
    registered = await client.post(
        '/auth/register',
        json={'email': 'other@mail.ru', 'password': 'secret', 'nickname': 'other'},
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None
    confirmation = next(item for item in InMemEmailConfirmationRepo.DB.values() if item.user_id == other.id)
    confirmed = await client.post('/auth/confirm', json={'token': confirmation.token})
    logged_in = await client.post('/auth/login', json={'email': 'other@mail.ru', 'password': 'secret'})
    other_headers = {'Authorization': f'Bearer {logged_in.json()["access_token"]}'}
    other_completed = await client.post(
        '/users/me/completed',
        headers=other_headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    second = await client.put(
        f'/games/{catalog.planescape.uuid}/rating',
        headers=other_headers,
        json={'score': scores[1]},
    )
    card = await client.get(f'/games/{catalog.planescape.uuid}')

    assert completed.status_code == HTTPStatus.CREATED
    assert first.status_code == HTTPStatus.OK
    assert registered.status_code == HTTPStatus.CREATED
    assert confirmed.status_code == HTTPStatus.NO_CONTENT
    assert other_completed.status_code == HTTPStatus.CREATED
    assert second.status_code == HTTPStatus.OK
    assert card.status_code == HTTPStatus.OK
    assert card.json()['users_score'] == sum(scores) / len(scores)
    assert card.json()['ratings_count'] == len(scores)
    assert card.json()['user_score'] is None


async def test_get_game_returns_the_callers_score(client: AsyncClient, access_token: str, catalog: Catalog) -> None:
    """A token adds that user's score. Without a token, and for a user who did not score, the field is null."""
    score = 8
    owner_headers = {'Authorization': f'Bearer {access_token}'}
    completed = await client.post(
        '/users/me/completed',
        headers=owner_headers,
        json={'game_uuid': str(catalog.disco.uuid)},
    )
    rated = await client.put(
        f'/games/{catalog.disco.uuid}/rating',
        headers=owner_headers,
        json={'score': score},
    )
    own = await client.get(f'/games/{catalog.disco.uuid}', headers=owner_headers)
    anonymous = await client.get(f'/games/{catalog.disco.uuid}')
    registered = await client.post(
        '/auth/register',
        json={'email': 'other@mail.ru', 'password': 'secret', 'nickname': 'other'},
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None
    confirmation = next(item for item in InMemEmailConfirmationRepo.DB.values() if item.user_id == other.id)
    confirmed = await client.post('/auth/confirm', json={'token': confirmation.token})
    logged_in = await client.post('/auth/login', json={'email': 'other@mail.ru', 'password': 'secret'})
    stranger = await client.get(
        f'/games/{catalog.disco.uuid}',
        headers={'Authorization': f'Bearer {logged_in.json()["access_token"]}'},
    )
    broken = await client.get(f'/games/{catalog.disco.uuid}', headers={'Authorization': 'Bearer not-a-token'})

    assert completed.status_code == HTTPStatus.CREATED
    assert rated.status_code == HTTPStatus.OK
    assert registered.status_code == HTTPStatus.CREATED
    assert confirmed.status_code == HTTPStatus.NO_CONTENT
    assert own.status_code == HTTPStatus.OK
    assert own.json()['user_score'] == score
    assert own.json()['users_score'] == float(score)
    assert anonymous.status_code == HTTPStatus.OK
    assert anonymous.json()['user_score'] is None
    assert stranger.status_code == HTTPStatus.OK
    assert stranger.json()['user_score'] is None
    assert stranger.json()['users_score'] == float(score)
    assert broken.status_code == HTTPStatus.UNAUTHORIZED
    assert broken.json() == {'detail': 'Invalid token'}


async def test_get_game_unknown_uuid_returns_404(client: AsyncClient) -> None:
    """An unknown uuid returns 404."""
    missing_uuid = UUID('00000000-0000-0000-0000-000000000099')

    response = await client.get(f'/games/{missing_uuid}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={missing_uuid} not found'}


async def test_get_game_hidden_returns_404(client: AsyncClient, catalog: Catalog) -> None:
    """A hidden game is missing from the catalog."""
    response = await client.get(f'/games/{catalog.hidden.uuid}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={catalog.hidden.uuid} not found'}


async def test_get_game_rejects_non_uuid(client: AsyncClient) -> None:
    """A non-uuid path is rejected before lookup."""
    response = await client.get('/games/not-a-uuid')

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
