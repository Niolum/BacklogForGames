import logging
from pathlib import Path
from typing import Final, Literal

from config import settings
from .utils import JsonFormatter, SimpleFormatter


def get_file_log_handler(
    path: Path,
    formatter_type: Literal['json', 'simple'] = 'json',
) -> logging.FileHandler:
    """Получение файлового хендлера для логов."""
    file_handler = logging.FileHandler(path, encoding='utf-8')
    formatter: logging.Formatter = JsonFormatter()
    if formatter_type == 'simple':
        formatter = SimpleFormatter('%(asctime)s [%(levelname)s] %(message)s')

    file_handler.setFormatter(formatter)
    return file_handler


logs_path = Path(settings.logs_path)
logs_path.mkdir(parents=True, exist_ok=True)
formatter_type: Final = 'json' if not settings.logging_simple_fmt else 'simple'


logger = logging.getLogger('backlogs_domain')
logger.setLevel(settings.logging_level)
logger.addHandler(get_file_log_handler(logs_path / 'app.log', formatter_type))
