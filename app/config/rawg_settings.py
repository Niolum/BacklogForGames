from pydantic import HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RawgSettings(BaseSettings):
    """RAWG settings loaded from RAWG_CONFIG__ environment variables."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='RAWG_CONFIG__',
        extra='ignore',
        validate_default=True,
        env_parse_none_str='None',
    )

    api_key: SecretStr = SecretStr('')
    base_url: HttpUrl = HttpUrl('https://api.rawg.io/api')

    @field_validator('api_key')
    @classmethod
    def api_key_is_set(cls, api_key: SecretStr) -> SecretStr:
        """The RAWG key comes from the environment and is not stored in code."""
        if api_key.get_secret_value() == '':
            msg = 'RAWG API key is empty'
            raise ValueError(msg)
        return api_key


rawg_settings = RawgSettings()
