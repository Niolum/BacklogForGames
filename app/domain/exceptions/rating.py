from .base import BacklogGamesConflictError, NotFoundError


class RatingNotFoundError(NotFoundError):
    """Rating not found error"""


class GameNotCompletedError(BacklogGamesConflictError):
    """Game is not in the user's completed list"""
