from .base import BadRequestError, NotFoundError


class EmailConfirmationNotFoundError(NotFoundError):
    """EmailConfirmation not found error"""


class EmailCofirmError(BadRequestError):
    """Email confrim error"""


class EmailAlreadyConfrimedError(BadRequestError):
    """Email already confirmed"""
