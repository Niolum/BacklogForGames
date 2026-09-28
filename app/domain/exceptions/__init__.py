from .auth import AuthError
from .base import (
    BacklogGamesConflictError,
    BacklogGamesPermissionError,
    BadRequestError,
    NotFoundError,
    TooManyRequests,
)
from .email_confirmation import EmailAlreadyConfrimedError, EmailCofirmError, EmailConfirmationNotFoundError
from .user import UserNotFoundError


__all__ = (
    'AuthError',
    'BacklogGamesConflictError',
    'BacklogGamesPermissionError',
    'BadRequestError',
    'EmailAlreadyConfrimedError',
    'EmailCofirmError',
    'EmailConfirmationNotFoundError',
    'NotFoundError',
    'TooManyRequests',
    'UserNotFoundError',
)
