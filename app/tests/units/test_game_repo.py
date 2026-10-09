from uuid import UUID

import pytest

from adapters.databases.in_memory.repositories.games.game import InMemGameRepo
from adapters.databases.in_memory.repositories.genres.genre import InMemGenreRepo
from domain.exceptions import GameNotFoundError, GenreNotFoundError
from domain.models import Game, Genre


async def test_game_repo_stores_genres_with_the_game(game: Game, genre: Genre, strategy_genre: Genre) -> None:
    """Create and read return the game with its genres."""
    await InMemGenreRepo().create(genre)
    await InMemGenreRepo().create(strategy_genre)
    repo = InMemGameRepo()
    await repo.create(game.model_copy(update={'genres': [strategy_genre, genre, genre]}))

    stored = await repo.get_by_id(game.id)

    assert stored is not None
    assert await repo.get_by_uuid(game.uuid) == stored
    assert [item.name for item in stored.genres] == ['RPG', 'Strategy']


async def test_game_repo_create_rejects_unknown_genre(game: Game) -> None:
    """A game is not stored when one of its genres is missing."""
    repo = InMemGameRepo()

    with pytest.raises(GenreNotFoundError, match='Genre with id=9 not found'):
        await repo.create(game.model_copy(update={'genres': [Genre(id=9, name='Missing')]}))

    assert await repo.get_by_id(game.id) is None


async def test_game_repo_update_replaces_genres(game: Game, genre: Genre, strategy_genre: Genre) -> None:
    """Update changes the title and replaces the genre list."""
    await InMemGenreRepo().create(genre)
    await InMemGenreRepo().create(strategy_genre)
    repo = InMemGameRepo()
    await repo.create(game.model_copy(update={'genres': [genre, strategy_genre]}))

    await repo.update(game.model_copy(update={'title': 'Torment', 'genres': [strategy_genre]}))

    stored = await repo.get_by_id(game.id)
    assert stored is not None
    assert stored.title == 'Torment'
    assert [item.name for item in stored.genres] == ['Strategy']
    assert await InMemGenreRepo().has_games(genre.id) is False
    assert await InMemGenreRepo().has_games(strategy_genre.id) is True


async def test_game_repo_update_missing_game_raises(game: Game) -> None:
    """Update of an unknown id raises not found."""
    with pytest.raises(GameNotFoundError, match='Game with id=1 not found'):
        await InMemGameRepo().update(game)


async def test_game_repo_get_by_id_or_raise_returns_game(game: Game) -> None:
    """A stored id and uuid are returned, and unknown keys raise not found."""
    repo = InMemGameRepo()
    await repo.create(game)
    missing_id = game.id + 1
    missing_uuid = UUID('00000000-0000-0000-0000-000000000099')

    assert await repo.get_by_id_or_raise(game.id) == game
    assert await repo.get_by_uuid_or_raise(game.uuid) == game

    with pytest.raises(GameNotFoundError, match=f'Game with id={missing_id} not found'):
        await repo.get_by_id_or_raise(missing_id)
    with pytest.raises(GameNotFoundError, match=f'Game with uuid={missing_uuid} not found'):
        await repo.get_by_uuid_or_raise(missing_uuid)


async def test_game_repo_page_filters_published_games_by_genre_and_title(
    game: Game,
    second_game: Game,
    third_game: Game,
    hidden_game: Game,
    genre: Genre,
    strategy_genre: Genre,
) -> None:
    """The page keeps published games that match the genre and the title, ordered by title."""
    await InMemGenreRepo().create(genre)
    await InMemGenreRepo().create(strategy_genre)
    repo = InMemGameRepo()
    await repo.create(third_game.model_copy(update={'genres': [genre]}))
    await repo.create(game.model_copy(update={'genres': [genre, strategy_genre]}))
    await repo.create(second_game.model_copy(update={'genres': [strategy_genre]}))
    await repo.create(hidden_game.model_copy(update={'genres': [genre]}))

    page = await repo.get_page(genre_id=genre.id, query='plan', limit=1, offset=0)
    rest = await repo.get_page(limit=10, offset=0)

    published = ['Disco Elysium', 'Planescape', 'Torment']
    assert page.total == 1
    assert [item.title for item in page.items] == ['Planescape']
    assert [item.title for item in rest.items] == published
    assert rest.total == len(published)


async def test_game_repo_page_returns_the_requested_slice(
    game: Game,
    second_game: Game,
    third_game: Game,
) -> None:
    """Offset and limit cut the published list and leave the total unchanged."""
    repo = InMemGameRepo()
    await repo.create(third_game)
    await repo.create(game)
    await repo.create(second_game)

    stored = [game, second_game, third_game]
    page = await repo.get_page(limit=1, offset=1)

    assert page.total == len(stored)
    assert [item.title for item in page.items] == ['Planescape']


async def test_game_repo_get_next_id_follows_the_highest_id(game: Game) -> None:
    """The next id is one greater than the highest stored id."""
    repo = InMemGameRepo()
    assert await repo.get_next_id() == 1

    await repo.create(game)

    assert await repo.get_next_id() == game.id + 1
