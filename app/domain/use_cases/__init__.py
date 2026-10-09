from .auth import (
    authenticate_admin,
    confirm_email,
    get_admin_user,
    get_current_user,
    login,
    register_user,
    resend_confirmation_email,
)
from .games import get_game_by_uuid, get_games
from .genres import create_genre, delete_genre, get_genre_by_id, get_genres, update_genre
from .users import delete_avatar, get_user_by_uuid, update_profile, upload_avatar


__all__ = [
    'authenticate_admin',
    'confirm_email',
    'create_genre',
    'delete_avatar',
    'delete_genre',
    'get_admin_user',
    'get_current_user',
    'get_game_by_uuid',
    'get_games',
    'get_genre_by_id',
    'get_genres',
    'get_user_by_uuid',
    'login',
    'register_user',
    'resend_confirmation_email',
    'update_genre',
    'update_profile',
    'upload_avatar',
]
