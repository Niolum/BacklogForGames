from fastapi import APIRouter, Response, status


user_router = APIRouter(prefix='/users', tags=['User'])


@user_router.get('')
async def hello_world_handler():
    """Hello world!"""
    return Response(status_code=status.HTTP_200_OK)
