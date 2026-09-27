from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSettings(BaseSettings):
    """SMTP settings loaded from EMAIL_CONFIG__ environment variables."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='EMAIL_CONFIG__',
        extra='ignore',
        validate_default=True,
        env_parse_none_str='None',
    )

    host: str = 'localhost'
    port: int = 587
    username: str | None = None
    password: str | None = None
    from_email: EmailStr = 'noreply@example.com'
    starttls: bool = True


email_settings = EmailSettings()
