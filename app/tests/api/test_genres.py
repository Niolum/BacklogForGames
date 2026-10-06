from http import HTTPStatus

from httpx import AsyncClient

from domain.models import Genre


async def test_list_genres_is_empty(client: AsyncClient) -> None:
    """The catalog is an empty list when no genres are stored."""
    response = await client.get('/genres')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


async def test_list_genres_returns_every_genre_without_token(
    client: AsyncClient,
    stored_genre: Genre,
    stored_strategy_genre: Genre,
) -> None:
    """Anyone can read the catalog, ordered by id."""
    response = await client.get('/genres')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            'id': stored_genre.id,
            'name': stored_genre.name,
            'description': stored_genre.description,
        },
        {
            'id': stored_strategy_genre.id,
            'name': stored_strategy_genre.name,
            'description': None,
        },
    ]


async def test_get_genre_returns_one_genre(client: AsyncClient, stored_genre: Genre) -> None:
    """A known id returns that genre."""
    response = await client.get(f'/genres/{stored_genre.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': stored_genre.id,
        'name': 'RPG',
        'description': 'Role-playing',
    }


async def test_get_genre_unknown_id_returns_404(client: AsyncClient, stored_genre: Genre) -> None:
    """An unknown id returns 404."""
    missing_id = stored_genre.id + 1

    response = await client.get(f'/genres/{missing_id}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Genre with id={missing_id} not found'}


async def test_get_genre_rejects_non_integer_id(client: AsyncClient) -> None:
    """A non-integer id is rejected before lookup."""
    response = await client.get('/genres/abc')

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
