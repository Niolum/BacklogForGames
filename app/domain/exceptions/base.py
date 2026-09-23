class BacklogGamesError(Exception):
    """Base domain exception from which all domain errors inherit."""

    def __str__(self) -> str:
        """String representation

        Uses the exception class's docstring if no message is specified.
        """
        return super().__str__() or self.__class__.__doc__ or ''


class NotFoundError(BacklogGamesError):
    """Object not found"""


class BacklogGamesPermissionError(BacklogGamesError):
    """Permission error"""


class BacklogGamesConflictError(BacklogGamesError):
    """Conflict error"""


class BadRequestError(BacklogGamesError):
    """Error in the request"""


class TooManyRequests(BacklogGamesError):
    """Too many requests error"""
