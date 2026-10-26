from collections.abc import Mapping
from uuid import UUID

from fastapi import APIRouter, Query, Response, UploadFile, status

from domain.constants import DEFAULT_LIMIT
from domain.models import UserGamePage, UserProfile
from domain.services import AddUserGameData, UpdateProfileData
from domain.use_cases import (
    add_to_backlog,
    add_to_completed,
    delete_avatar,
    get_user_backlog,
    get_user_completed,
    get_user_profile,
    remove_from_list,
    update_profile,
    upload_avatar,
)
from entrypoints.fastapi.dependencies import CurrentUser
from entrypoints.fastapi.schemas.request import AddUserGameRequestSchema, UpdateProfileRequestSchema
from entrypoints.fastapi.schemas.response import (
    CompletedGameItemResponseSchema,
    CompletedGamePageResponseSchema,
    PublicUserResponseSchema,
    UserGameItemResponseSchema,
    UserGamePageResponseSchema,
    UserMeResponseSchema,
)


user_router = APIRouter(prefix='/users', tags=['User'])


@user_router.get('/me')
async def current_user_handler(current_user: CurrentUser) -> UserMeResponseSchema:
    """Return the current user's profile."""
    profile = await get_user_profile(current_user.uuid)
    return _user_me(profile)


@user_router.patch('/me')
async def update_current_user_handler(
    current_user: CurrentUser,
    request_data: UpdateProfileRequestSchema,
) -> UserMeResponseSchema:
    """Update nickname, date of birth and about of the current user."""
    data = UpdateProfileData.model_validate(request_data.model_dump(exclude_unset=True))
    user = await update_profile(current_user, data)
    profile = await get_user_profile(user.uuid)
    return _user_me(profile)


@user_router.post('/me/avatar')
async def upload_avatar_handler(current_user: CurrentUser, file: UploadFile) -> UserMeResponseSchema:
    """Store an avatar for the current user."""
    content = await file.read()
    user = await upload_avatar(current_user, content, file.content_type)
    profile = await get_user_profile(user.uuid)
    return _user_me(profile)


@user_router.delete('/me/avatar')
async def delete_avatar_handler(current_user: CurrentUser) -> Response:
    """Remove the avatar of the current user."""
    await delete_avatar(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.post('/me/backlog', status_code=status.HTTP_201_CREATED)
async def add_to_backlog_handler(current_user: CurrentUser, request_data: AddUserGameRequestSchema) -> Response:
    """Add a game to the current user's backlog."""
    data = AddUserGameData.model_validate(request_data.model_dump())
    await add_to_backlog(current_user, data)
    return Response(status_code=status.HTTP_201_CREATED)


@user_router.post('/me/completed', status_code=status.HTTP_201_CREATED)
async def add_to_completed_handler(current_user: CurrentUser, request_data: AddUserGameRequestSchema) -> Response:
    """Mark a game completed for the current user."""
    data = AddUserGameData.model_validate(request_data.model_dump())
    await add_to_completed(current_user, data)
    return Response(status_code=status.HTTP_201_CREATED)


@user_router.delete('/me/games/{game_uuid}')
async def remove_from_list_handler(current_user: CurrentUser, game_uuid: UUID) -> Response:
    """Remove a game from the current user's backlog or completed list."""
    await remove_from_list(current_user, game_uuid)
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


@user_router.get('/{user_uuid}/completed', response_model=CompletedGamePageResponseSchema)
async def user_completed_handler(
    user_uuid: UUID,
    limit: int = Query(default=DEFAULT_LIMIT, ge=1),
    offset: int = Query(default=0, ge=0),
) -> CompletedGamePageResponseSchema:
    """Return one page of the user's completed games and the owner's score. No token is required."""
    page = await get_user_completed(user_uuid, limit=limit, offset=offset)
    return CompletedGamePageResponseSchema(
        items=[
            CompletedGameItemResponseSchema.model_validate(item.game.model_dump() | {'user_score': item.user_score})
            for item in page.items
        ],
        total=page.total,
    )


def _user_game_page(page: UserGamePage) -> UserGamePageResponseSchema:
    """Map a page of games to cover, title and genres."""
    return UserGamePageResponseSchema(
        items=[UserGameItemResponseSchema.model_validate(game.model_dump()) for game in page.items],
        total=page.total,
    )


@user_router.get('/{user_uuid}')
async def public_user_handler(user_uuid: UUID) -> PublicUserResponseSchema:
    """Return a public profile without email and password."""
    profile = await get_user_profile(user_uuid)
    return PublicUserResponseSchema.model_validate(_profile_payload(profile))


def _user_me(profile: UserProfile) -> UserMeResponseSchema:
    """Map a profile to the current user's response."""
    return UserMeResponseSchema.model_validate(_profile_payload(profile))


def _profile_payload(profile: UserProfile) -> Mapping[str, object]:
    """Merge the user row with the counted list sizes."""
    return profile.user.model_dump() | {
        'backlog_count': profile.counts.backlog_count,
        'completed_count': profile.counts.completed_count,
    }
