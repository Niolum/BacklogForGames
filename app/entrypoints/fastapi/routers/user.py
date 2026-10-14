from uuid import UUID

from fastapi import APIRouter, Query, Response, UploadFile, status

from domain.constants import DEFAULT_LIMIT
from domain.models import UserGamePage
from domain.services import UpdateProfileData
from domain.use_cases import (
    delete_avatar,
    get_user_backlog,
    get_user_by_uuid,
    get_user_completed,
    update_profile,
    upload_avatar,
)
from entrypoints.fastapi.dependencies import CurrentUser
from entrypoints.fastapi.schemas.request import UpdateProfileRequestSchema
from entrypoints.fastapi.schemas.response import (
    PublicUserResponseSchema,
    UserGameItemResponseSchema,
    UserGamePageResponseSchema,
    UserMeResponseSchema,
)


user_router = APIRouter(prefix='/users', tags=['User'])


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


@user_router.post('/me/avatar')
async def upload_avatar_handler(current_user: CurrentUser, file: UploadFile) -> UserMeResponseSchema:
    """Store an avatar for the current user."""
    content = await file.read()
    user = await upload_avatar(current_user, content, file.content_type)
    return UserMeResponseSchema.model_validate(user.model_dump())


@user_router.delete('/me/avatar')
async def delete_avatar_handler(current_user: CurrentUser) -> Response:
    """Remove the avatar of the current user."""
    await delete_avatar(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.get('/{user_uuid}/backlog', response_model=UserGamePageResponseSchema)
async def user_backlog_handler(
    user_uuid: UUID,
    limit: int = Query(default=DEFAULT_LIMIT, ge=1),
    offset: int = Query(default=0, ge=0),
) -> UserGamePageResponseSchema:
    """Return one page of the user's backlog. No token is required."""
    page = await get_user_backlog(user_uuid, limit=limit, offset=offset)
    return _user_game_page(page)


@user_router.get('/{user_uuid}/completed', response_model=UserGamePageResponseSchema)
async def user_completed_handler(
    user_uuid: UUID,
    limit: int = Query(default=DEFAULT_LIMIT, ge=1),
    offset: int = Query(default=0, ge=0),
) -> UserGamePageResponseSchema:
    """Return one page of the user's completed games. No token is required."""
    page = await get_user_completed(user_uuid, limit=limit, offset=offset)
    return _user_game_page(page)


def _user_game_page(page: UserGamePage) -> UserGamePageResponseSchema:
    """Map a page of games to cover, title and genres."""
    return UserGamePageResponseSchema(
        items=[UserGameItemResponseSchema.model_validate(game.model_dump()) for game in page.items],
        total=page.total,
    )


@user_router.get('/{user_uuid}')
async def public_user_handler(user_uuid: UUID) -> PublicUserResponseSchema:
    """Return a public profile without email and password."""
    user = await get_user_by_uuid(user_uuid)
    return PublicUserResponseSchema.model_validate(user.model_dump())
