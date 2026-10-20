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
from .game import GameNotFoundError, UploadGameCoverError
from .genre import GenreHasGamesError, GenreNameAlreadyTakenError, GenreNotFoundError
from .rating import RatingNotFoundError
from .user import UploadUserAvatarError, UserNicknameAlreadyTakenError, UserNotFoundError
from .user_game import UserGameAlreadyListedError, UserGameNotFoundError


__all__ = (
    'AuthError',
    'BacklogGamesConflictError',
    'BacklogGamesPermissionError',
    'BadRequestError',
    'EmailAlreadyConfrimedError',
    'EmailCofirmError',
    'EmailConfirmationNotFoundError',
    'GameNotFoundError',
    'GenreHasGamesError',
    'GenreNameAlreadyTakenError',
    'GenreNotFoundError',
    'InvalidFilePath',
    'NotFoundError',
    'RatingNotFoundError',
    'TooManyRequests',
    'UploadFileTypeError',
    'UploadGameCoverError',
    'UploadUserAvatarError',
    'UserGameAlreadyListedError',
    'UserGameNotFoundError',
    'UserNicknameAlreadyTakenError',
    'UserNotFoundError',
)
