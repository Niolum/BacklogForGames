from datetime import date
from typing import Self

from pydantic import BaseModel, Field, model_validator


class UpdateProfileRequestSchema(BaseModel):
    """Fields the current user can change."""

    nickname: str | None = Field(default=None, min_length=1, max_length=255, description='User nickname')
    date_birth: date | None = Field(default=None, description='Date of birth user')
    about: str | None = Field(default=None, description='Information about yourself')

    @model_validator(mode='after')
    def reject_null_nickname(self) -> Self:
        """Reject an explicit null nickname. An omitted nickname stays unchanged."""
        if 'nickname' in self.model_fields_set and self.nickname is None:
            msg = 'Nickname cannot be null'
            raise ValueError(msg)
        return self
