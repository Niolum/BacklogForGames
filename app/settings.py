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


setting = Setting()
