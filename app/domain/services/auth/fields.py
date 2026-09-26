from typing import Annotated

from pydantic import AfterValidator, EmailStr

from domain.constants import PASSWORD_MAX_BYTES


def lowercase_email(value: str) -> str:
    """Lowercase the whole address after EmailStr normalization."""
    return value.lower()


def validate_password_length(value: str) -> str:
    """Reject a password that exceeds the bcrypt limit of 72 bytes."""
    if len(value.encode('utf-8')) > PASSWORD_MAX_BYTES:
        msg = 'Password must be at most 72 bytes'
        raise ValueError(msg)
    return value


EmailField = Annotated[EmailStr, AfterValidator(lowercase_email)]
PasswordField = Annotated[str, AfterValidator(validate_password_length)]
