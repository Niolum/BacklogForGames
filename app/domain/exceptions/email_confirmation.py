from .base import BadRequestError, NotFoundError


class EmailConfirmationNotFoundError(NotFoundError):
    """EmailConfirmation not found error"""


class EmailCofirmError(BadRequestError):
    """Email confrim error"""
