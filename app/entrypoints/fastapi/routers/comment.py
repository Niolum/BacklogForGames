from uuid import UUID

from fastapi import APIRouter

from domain.services import UpdateCommentData
from domain.use_cases import update_comment
from entrypoints.fastapi.dependencies import CurrentUser
from entrypoints.fastapi.schemas.request import UpdateCommentRequestSchema
from entrypoints.fastapi.schemas.response import CommentResponseSchema


comment_router = APIRouter(prefix='/comments', tags=['Comment'])


@comment_router.patch('/{comment_uuid}', response_model=CommentResponseSchema)
async def update_comment_handler(
    current_user: CurrentUser,
    comment_uuid: UUID,
    request_data: UpdateCommentRequestSchema,
) -> CommentResponseSchema:
    """Replace the current user's comment text."""
    data = UpdateCommentData.model_validate(request_data.model_dump())
    comment = await update_comment(current_user, comment_uuid, data)
    return CommentResponseSchema.model_validate(comment.model_dump())
