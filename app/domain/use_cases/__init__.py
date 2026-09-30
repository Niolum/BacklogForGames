from .auth import confirm_email, get_current_user, login, register_user, resend_confirmation_email
from .users import delete_avatar, get_user_by_uuid, update_profile, upload_avatar


__all__ = [
    'confirm_email',
    'delete_avatar',
    'get_current_user',
    'get_user_by_uuid',
    'login',
    'register_user',
    'resend_confirmation_email',
    'update_profile',
    'upload_avatar',
]
