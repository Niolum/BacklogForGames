from .auth import AuthError
from .base import (
    BacklogGamesConflictError,
    BacklogGamesPermissionError,
    BadRequestError,
    NotFoundError,
    TooManyRequests,
)
from .email_confirmation import EmailAlreadyConfrimedError, EmailCofirmError, EmailConfirmationNotFoundError
from .file import InvalidFilePath, UploadFileTypeError
from .genre import GenreNotFoundError
from .user import UploadUserAvatarError, UserNicknameAlreadyTakenError, UserNotFoundError


__all__ = (
    'AuthError',
    'BacklogGamesConflictError',
    'BacklogGamesPermissionError',
    'BadRequestError',
    'EmailAlreadyConfrimedError',
    'EmailCofirmError',
    'EmailConfirmationNotFoundError',
    'GenreNotFoundError',
    'InvalidFilePath',
    'NotFoundError',
    'TooManyRequests',
    'UploadFileTypeError',
    'UploadUserAvatarError',
    'UserNicknameAlreadyTakenError',
    'UserNotFoundError',
)
