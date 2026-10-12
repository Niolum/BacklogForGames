from .base import BadRequestError, NotFoundError


class GameNotFoundError(NotFoundError):
    """Game not found error"""


class UploadGameCoverError(BadRequestError):
    """Upload game cover error"""
