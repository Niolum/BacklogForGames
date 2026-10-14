from .base import BacklogGamesConflictError, NotFoundError


class UserGameNotFoundError(NotFoundError):
    """User game not found error"""


class UserGameAlreadyListedError(BacklogGamesConflictError):
    """User game already listed error"""
