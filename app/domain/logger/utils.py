import json
import logging

from .encoder import jsonable_encoder


standard_attrs = {
    'name',
    'msg',
    'args',
    'levelname',
    'levelno',
    'pathname',
    'filename',
    'module',
    'exc_info',
    'exc_text',
    'stack_info',
    'lineno',
    'funcName',
    'created',
    'msecs',
    'relativeCreated',
    'thread',
    'threadName',
    'processName',
    'process',
    'message',
    'asctime',
}


class JsonFormatter(logging.Formatter):
    """JSON formatter"""

    def format(self, record):
        """Форматирует лог-запись в JSON-строку."""
        log_record = {
            'time': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'lineno': record.lineno,
            'funcName': record.funcName,
        }

        for key, value in record.__dict__.items():
            if key in standard_attrs:
                continue
            log_record[key] = jsonable_encoder(value)

        return json.dumps(log_record, ensure_ascii=False)


class SimpleFormatter(logging.Formatter):
    """Simple str formatter"""

    def format(self, record):
        """Format"""
        extra = dict()
        omit_keys = ('taskName',)
        for key, value in record.__dict__.items():
            if key in standard_attrs or key in omit_keys:
                continue
            extra[key] = jsonable_encoder(value)

        return super().format(record) + (f' [EXTRA] {extra}' if extra else '')
