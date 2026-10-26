from .auth import LoginResponseSchema
from .comment import CommentPageResponseSchema, CommentResponseSchema
from .error import ErrorResponseSchema
from .game import GameCardResponseSchema, GamePageResponseSchema, GameResponseSchema
from .genre import GenreResponseSchema
from .rating import RatingResponseSchema
from .user import PublicUserResponseSchema, UserMeResponseSchema
from .user_game import UserGameItemResponseSchema, UserGamePageResponseSchema


__all__ = (
    'CommentPageResponseSchema',
    'CommentResponseSchema',
    'ErrorResponseSchema',
    'GameCardResponseSchema',
    'GamePageResponseSchema',
    'GameResponseSchema',
    'GenreResponseSchema',
    'LoginResponseSchema',
    'PublicUserResponseSchema',
    'RatingResponseSchema',
    'UserGameItemResponseSchema',
    'UserGamePageResponseSchema',
    'UserMeResponseSchema',
)
