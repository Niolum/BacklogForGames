from .base import BacklogGamesConflictError, BadRequestError, NotFoundError


class UserNotFoundError(NotFoundError):
    """User not found exception"""


class UserNicknameAlreadyTakenError(BacklogGamesConflictError):
    """User nickname already taken error"""


class UploadUserAvatarError(BadRequestError):
    """Upload user avatar error"""
