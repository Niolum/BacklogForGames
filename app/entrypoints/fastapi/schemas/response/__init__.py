from .auth import LoginResponseSchema
from .error import ErrorResponseSchema
from .game import GameCardResponseSchema, GamePageResponseSchema, GameResponseSchema
from .genre import GenreResponseSchema
from .user import PublicUserResponseSchema, UserMeResponseSchema
from .user_game import UserGameItemResponseSchema, UserGamePageResponseSchema


__all__ = (
    'ErrorResponseSchema',
    'GameCardResponseSchema',
    'GamePageResponseSchema',
    'GameResponseSchema',
    'GenreResponseSchema',
    'LoginResponseSchema',
    'PublicUserResponseSchema',
    'UserGameItemResponseSchema',
    'UserGamePageResponseSchema',
    'UserMeResponseSchema',
)
