from .auth import (
    authenticate_admin,
    confirm_email,
    get_admin_user,
    get_current_user,
    login,
    register_user,
    resend_confirmation_email,
)
from .comments import create_comment, delete_comment, get_game_comments, update_comment
from .games import create_game, get_game_by_uuid, get_game_card, get_games, update_game
from .genres import create_genre, delete_genre, get_genre_by_id, get_genres, update_genre
from .ratings import set_rating
from .rawg import import_catalog
from .user_games import add_to_backlog, add_to_completed, get_user_backlog, get_user_completed, remove_from_list
from .users import delete_avatar, get_user_profile, update_profile, upload_avatar


__all__ = [
    'add_to_backlog',
    'add_to_completed',
    'authenticate_admin',
    'confirm_email',
    'create_comment',
    'create_game',
    'create_genre',
    'delete_avatar',
    'delete_comment',
    'delete_genre',
    'get_admin_user',
    'get_current_user',
    'get_game_by_uuid',
    'get_game_card',
    'get_game_comments',
    'get_games',
    'get_genre_by_id',
    'get_genres',
    'get_user_backlog',
    'get_user_completed',
    'get_user_profile',
    'import_catalog',
    'login',
    'register_user',
    'remove_from_list',
    'resend_confirmation_email',
    'set_rating',
    'update_comment',
    'update_game',
    'update_genre',
    'update_profile',
    'upload_avatar',
]
