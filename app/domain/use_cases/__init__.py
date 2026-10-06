from .auth import (
    authenticate_admin,
    confirm_email,
    get_admin_user,
    get_current_user,
    login,
    register_user,
    resend_confirmation_email,
)
from .genres import get_genre_by_id, get_genres
from .users import delete_avatar, get_user_by_uuid, update_profile, upload_avatar


__all__ = [
    'authenticate_admin',
    'confirm_email',
    'delete_avatar',
    'get_admin_user',
    'get_current_user',
    'get_genre_by_id',
    'get_genres',
    'get_user_by_uuid',
    'login',
    'register_user',
    'resend_confirmation_email',
    'update_profile',
    'upload_avatar',
]
