from .auth import AuthError
from .base import (
    BacklogGamesConflictError,
    BacklogGamesPermissionError,
    BadRequestError,
    NotFoundError,
    TooManyRequests,
)
from .email_confirmation import EmailCofirmError, EmailConfirmationNotFoundError
from .user import UserNotFoundError


__all__ = (
    'AuthError',
    'BacklogGamesConflictError',
    'BacklogGamesPermissionError',
    'BadRequestError',
    'EmailCofirmError',
    'EmailConfirmationNotFoundError',
    'NotFoundError',
    'TooManyRequests',
    'UserNotFoundError',
)
