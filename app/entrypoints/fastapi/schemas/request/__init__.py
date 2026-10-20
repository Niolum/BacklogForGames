from .auth import (
    ConfirmEmailRequestSchema,
    LoginRequestSchema,
    ResendConfirmationRequestSchema,
    UserRegisterRequestSchema,
)
from .rating import SetRatingRequestSchema
from .user import UpdateProfileRequestSchema
from .user_game import AddUserGameRequestSchema


__all__ = [
    'AddUserGameRequestSchema',
    'ConfirmEmailRequestSchema',
    'LoginRequestSchema',
    'ResendConfirmationRequestSchema',
    'SetRatingRequestSchema',
    'UpdateProfileRequestSchema',
    'UserRegisterRequestSchema',
]
