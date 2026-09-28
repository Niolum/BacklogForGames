from fastapi import APIRouter, Response, status

from entrypoints.fastapi.dependencies import CurrentUser


user_router = APIRouter(prefix='/users', tags=['User'])


@user_router.get('')
async def hello_world_handler():
    """Hello world!"""
    return Response(status_code=status.HTTP_200_OK)


@user_router.get('/me')
async def current_user_handler(_current_user: CurrentUser) -> Response:
    """Require the current user. The profile body comes later."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)
