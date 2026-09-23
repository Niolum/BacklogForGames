from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SQLABaseRepo:
    """Base repository SQLAlchemy"""


    def __init__(self, session: 'AsyncSession'):
        self.session = session
