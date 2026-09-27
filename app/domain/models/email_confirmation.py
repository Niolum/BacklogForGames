from pydantic import AwareDatetime, BaseModel, Field


class EmailConfirmation(BaseModel):
    """Email confirmation token."""

    id: int
    user_id: int = Field(description='User')
    token: str = Field(description='Confirmation token')
    expires_at: AwareDatetime = Field(description='Token expiration time')
    used_at: AwareDatetime | None = Field(default=None, description='Token use time')
