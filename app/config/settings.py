import logging
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.constants import Environment


class Settings(BaseSettings):
    """Class for managing application settings via environment variables"""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='APP_CONFIG__',
        extra='ignore',
        validate_default=True,
        env_parse_none_str='None',
    )

    project_name: str = 'Backlog For Games'
    environment: Environment = Environment.development

    # DB
    db_alembic_url: PostgresDsn = PostgresDsn('postgresql+asyncpg://postgres:pass@backlogdb:5434/backlog_app')
    alchemy_pool_size: int = 5
    alchemy_pool_max_overflow: int = 10
    db_echo: bool = False
    db_schema_name: str = 'backlog_app'
    db_infra_schema: str = 'infra'

    default_timezone: ZoneInfo = ZoneInfo('Europe/Moscow')

    logs_path: Path = Path('/opt/backlogs/logs')
    logging_simple_fmt: bool = False
    logging_level: int = logging.INFO


settings = Settings()
