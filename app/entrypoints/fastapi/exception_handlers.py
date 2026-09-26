from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.types import HTTPExceptionHandler

from domain.exceptions import (
    AuthError,
    BacklogGamesConflictError,
    BacklogGamesPermissionError,
    BadRequestError,
    NotFoundError,
    TooManyRequests,
)
from entrypoints.fastapi.schemas.response import ErrorResponseSchema


def error_response(status_code: int, exc: Exception) -> JSONResponse:
    """Build a JSON error response from a domain exception."""
    body = ErrorResponseSchema(detail=str(exc))
    return JSONResponse(status_code=status_code, content=body.model_dump())


def _handler(status_code: int) -> HTTPExceptionHandler:
    """Create an exception handler that returns the given status code."""

    async def handle(_request: Request, exc: Exception) -> JSONResponse:
        return error_response(status_code, exc)

    return handle


def register_exception_handlers(app: FastAPI) -> None:
    """Map domain exceptions to HTTP responses."""
    app.add_exception_handler(AuthError, _handler(status.HTTP_401_UNAUTHORIZED))
    app.add_exception_handler(NotFoundError, _handler(status.HTTP_404_NOT_FOUND))
    app.add_exception_handler(BacklogGamesPermissionError, _handler(status.HTTP_403_FORBIDDEN))
    app.add_exception_handler(BadRequestError, _handler(status.HTTP_400_BAD_REQUEST))
    app.add_exception_handler(BacklogGamesConflictError, _handler(status.HTTP_409_CONFLICT))
    app.add_exception_handler(TooManyRequests, _handler(status.HTTP_429_TOO_MANY_REQUESTS))
