"""Module with settings for project"""

import os
from pathlib import Path

from dotenv import load_dotenv


class Setting:
    """This configuration used to get the database
      connection string from the environment variables.
    """
    BASE_DIR = Path(__file__).parent.parent.resolve()
    load_dotenv(os.path.join(BASE_DIR, ".env"))

    DB_USER: str | None = os.getenv("DB_USER")
    DB_PASSWORD: str | None=os.getenv("DB_PASSWORD")
    DB_HOST: str | None=os.getenv("DB_HOST")
    DB_NAME: str | None=os.getenv("DB_NAME")
    DB_CONFIG: str = os.getenv(
        "DB_CONFIG",
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}",
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "some_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    EMAIL: str = os.getenv("EMAIL", "admin@admin.ru")
    PASSWORD: str = os.getenv("PASSWORD", "12345")
    FIRST_NAME: str | None = os.getenv("FIRST_NAME", None)
    LAST_NAME: str | None = os.getenv("LAST_NAME", None)
    AVATAR: str | None = os.getenv("AVATAR", None)
    ABOUT: str | None = os.getenv("ABOUT", None)
    IS_SUPERUSER: bool = bool(os.getenv("IS_SUPERUSER", None))


setting = Setting()
