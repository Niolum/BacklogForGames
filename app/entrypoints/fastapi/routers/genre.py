from fastapi import APIRouter

from domain.use_cases import get_genre_by_id, get_genres
from entrypoints.fastapi.schemas.response import GenreResponseSchema


genre_router = APIRouter(prefix='/genres', tags=['Genre'])


@genre_router.get('')
async def list_genres_handler() -> list[GenreResponseSchema]:
    """Return every genre. No token is required."""
    genres = await get_genres()
    return [GenreResponseSchema.model_validate(genre.model_dump()) for genre in genres]


@genre_router.get('/{genre_id}')
async def genre_handler(genre_id: int) -> GenreResponseSchema:
    """Return one genre. An unknown id responds with 404."""
    genre = await get_genre_by_id(genre_id)
    return GenreResponseSchema.model_validate(genre.model_dump())
