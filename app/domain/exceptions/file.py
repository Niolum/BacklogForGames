from .base import BadRequestError


class UploadFileTypeError(BadRequestError):
    """Upload file type error"""


class InvalidFilePath(BadRequestError):
    """Invalid file path"""
