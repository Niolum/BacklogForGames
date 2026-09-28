from uuid import UUID

from fastapi import APIRouter, Response, status

from domain.services import UpdateProfileData
from domain.use_cases import get_user_by_uuid, update_profile
from entrypoints.fastapi.dependencies import CurrentUser
from entrypoints.fastapi.schemas.request import UpdateProfileRequestSchema
from entrypoints.fastapi.schemas.response import PublicUserResponseSchema, UserMeResponseSchema


user_router = APIRouter(prefix='/users', tags=['User'])


@user_router.get('')
async def hello_world_handler():
    """Hello world!"""
    return Response(status_code=status.HTTP_200_OK)


@user_router.get('/me')
async def current_user_handler(current_user: CurrentUser) -> UserMeResponseSchema:
    """Return the current user's profile."""
    return UserMeResponseSchema.model_validate(current_user.model_dump())


@user_router.patch('/me')
async def update_current_user_handler(
    current_user: CurrentUser,
    request_data: UpdateProfileRequestSchema,
) -> UserMeResponseSchema:
    """Update nickname, date of birth and about of the current user."""
    data = UpdateProfileData.model_validate(request_data.model_dump(exclude_unset=True))
    user = await update_profile(current_user, data)
    return UserMeResponseSchema.model_validate(user.model_dump())


@user_router.get('/{user_uuid}')
async def public_user_handler(user_uuid: UUID) -> PublicUserResponseSchema:
    """Return a public profile without email and password."""
    user = await get_user_by_uuid(user_uuid)
    return PublicUserResponseSchema.model_validate(user.model_dump())
