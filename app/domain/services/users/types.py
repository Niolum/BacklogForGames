from datetime import date
from typing import Self

from pydantic import BaseModel, Field, model_validator


class UpdateProfileData(BaseModel):
    """Fields a user can change on their own profile."""

    nickname: str | None = Field(default=None, min_length=1, max_length=255)
    date_birth: date | None = None
    about: str | None = None

    @model_validator(mode='after')
    def reject_null_nickname(self) -> Self:
        """Reject an explicit null nickname. An omitted nickname stays unchanged."""
        if 'nickname' in self.model_fields_set and self.nickname is None:
            msg = 'Nickname cannot be null'
            raise ValueError(msg)
        return self
