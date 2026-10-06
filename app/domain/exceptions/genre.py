from .base import BacklogGamesConflictError, NotFoundError


class GenreNotFoundError(NotFoundError):
    """Genre not found error"""


class GenreNameAlreadyTakenError(BacklogGamesConflictError):
    """Genre name already taken error"""


class GenreHasGamesError(BacklogGamesConflictError):
    """Genre is referenced by games and cannot be deleted"""
