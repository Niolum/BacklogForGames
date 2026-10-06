from http import HTTPStatus

import pytest
from httpx import AsyncClient
from starlette.requests import Request

from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from domain.exceptions import GenreHasGamesError
from domain.models import Genre
from entrypoints.fastapi.admin.genre import GenreAdmin


async def test_admin_create_form_edits_name_and_description(admin_client: AsyncClient) -> None:
    """The create form asks for the name and description."""
    response = await admin_client.get('/admin/genre/create')

    assert response.status_code == HTTPStatus.OK
    assert 'name="name"' in response.text
    assert 'name="description"' in response.text
    assert 'name="external_source"' not in response.text
    assert 'name="external_id"' not in response.text


async def test_admin_create_rejects_taken_name(admin_client: AsyncClient, stored_genre: Genre) -> None:
    """A taken name stays on the form and is not saved again."""
    response = await admin_client.post(
        '/admin/genre/create',
        data={'name': stored_genre.name, 'description': 'Another', 'save': 'Save'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Genre with name=RPG already exists' in response.text
    assert [genre.name for genre in await InMemGenreRepo().get_all()] == ['RPG']


async def test_admin_updates_name_and_description(client: AsyncClient, stored_genre: Genre) -> None:
    """The edit handler changes the name and description and keeps the external identity."""
    await InMemGenreRepo().update(stored_genre.model_copy(update={'external_source': 'igdb', 'external_id': '9'}))

    await GenreAdmin().update_model(
        _request(),
        str(stored_genre.id),
        {'name': 'Adventure', 'description': 'Story'},
    )
    stored = await InMemGenreRepo().get_by_id(stored_genre.id)
    listed = await client.get(f'/genres/{stored_genre.id}')

    assert stored is not None
    assert stored.name == 'Adventure'
    assert stored.description == 'Story'
    assert stored.external_source == 'igdb'
    assert stored.external_id == '9'
    assert listed.json() == {'id': stored_genre.id, 'name': 'Adventure', 'description': 'Story'}


async def test_admin_clears_description(stored_genre: Genre) -> None:
    """An empty description clears the stored text."""
    await GenreAdmin().update_model(
        _request(),
        str(stored_genre.id),
        {'name': stored_genre.name, 'description': ''},
    )
    stored = await InMemGenreRepo().get_by_id(stored_genre.id)

    assert stored is not None
    assert stored.description is None


async def test_admin_deletes_genre(client: AsyncClient, stored_genre: Genre) -> None:
    """Delete removes a genre that no game references."""
    await GenreAdmin().delete_model(_request(), str(stored_genre.id))
    listed = await client.get('/genres')

    assert listed.json() == []


async def test_admin_delete_rejects_genre_used_by_games(stored_genre: Genre) -> None:
    """Delete is refused while games reference the genre."""
    InMemGenreRepo.USED_BY_GAMES.add(stored_genre.id)

    with pytest.raises(GenreHasGamesError, match='cannot be deleted because games use it'):
        await GenreAdmin().delete_model(_request(), str(stored_genre.id))
    stored = await InMemGenreRepo().get_by_id(stored_genre.id)

    assert stored is not None
    assert stored.name == 'RPG'


def _request() -> Request:
    return Request({'type': 'http', 'method': 'POST', 'path': '/admin/genre', 'headers': []})
