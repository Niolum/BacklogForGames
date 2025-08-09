from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Class for managing application settings via environment variables"""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='APP_CONFIG__',
        extra='ignore',
        validate_default=True,
        env_parse_none_str='None',
    )

    # DB
    db_alembic_url: PostgresDsn = PostgresDsn('postgresql+asyncpg://postgres:password@localhost/backlogforgames')
    db_echo: bool = False



settings = Settings()
