from .base import BacklogGamesConflictError, NotFoundError


class UserNotFoundError(NotFoundError):
    """User not found exception"""


class UserNicknameAlreadyTakenError(BacklogGamesConflictError):
    """User nickname already taken error"""
