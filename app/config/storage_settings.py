from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseSettings):
    """File storage settings loaded from STORAGE_CONFIG__ environment variables."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='STORAGE_CONFIG__',
        extra='ignore',
        validate_default=True,
        env_parse_none_str='None',
    )

    local_root: Path = Path('/opt/backlogs/local_storage')
    s3_bucket: str = ''
    s3_access_key: str = ''
    s3_secret_key: str = ''
    s3_endpoint_url: str | None = None

    base_user_avatar_path: Path = Path('avatars')


storage_settings = StorageSettings()
