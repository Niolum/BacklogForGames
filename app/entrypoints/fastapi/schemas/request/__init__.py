from .auth import (
    ConfirmEmailRequestSchema,
    LoginRequestSchema,
    ResendConfirmationRequestSchema,
    UserRegisterRequestSchema,
)
from .comment import CreateCommentRequestSchema, UpdateCommentRequestSchema
from .rating import SetRatingRequestSchema
from .user import UpdateProfileRequestSchema
from .user_game import AddUserGameRequestSchema


__all__ = [
    'AddUserGameRequestSchema',
    'ConfirmEmailRequestSchema',
    'CreateCommentRequestSchema',
    'LoginRequestSchema',
    'ResendConfirmationRequestSchema',
    'SetRatingRequestSchema',
    'UpdateCommentRequestSchema',
    'UpdateProfileRequestSchema',
    'UserRegisterRequestSchema',
]
