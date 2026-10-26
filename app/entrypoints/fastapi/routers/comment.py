from uuid import UUID

from fastapi import APIRouter, Response, status

from domain.services import UpdateCommentData
from domain.use_cases import delete_comment, update_comment
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


@comment_router.delete('/{comment_uuid}')
async def delete_comment_handler(current_user: CurrentUser, comment_uuid: UUID) -> Response:
    """Remove the current user's comment."""
    await delete_comment(current_user, comment_uuid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
