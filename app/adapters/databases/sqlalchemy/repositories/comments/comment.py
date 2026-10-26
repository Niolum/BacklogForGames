from typing import override
from uuid import UUID

from sqlalchemy import func, select, text

from adapters.databases.sqlalchemy.models import CommentORM, UserORM
from adapters.databases.sqlalchemy.repositories.base import SQLABaseRepo
from domain.exceptions import CommentNotFoundError
from domain.interfaces.repositories import CommentRepo
from domain.models import Comment, CommentAuthor, CommentItem, CommentPage


class SQLACommentRepo(SQLABaseRepo, CommentRepo):
    """Implementing a comment repository using SQLAlchemy."""

    @override
    async def get_next_id(self) -> int:
        res = await self.session.execute(text("select nextval('comments_id_seq')"))
        return res.scalar_one()

    @override
    async def create(self, comment: Comment) -> None:
        self.session.add(CommentORM.from_model(comment))
        await self.session.flush()

    @override
    async def get_by_uuid(self, comment_uuid: UUID) -> Comment | None:
        result = await self.session.execute(select(CommentORM).where(CommentORM.uuid == comment_uuid))
        comment_orm = result.scalar_one_or_none()
        if comment_orm is None:
            return None
        return comment_orm.to_domain()

    @override
    async def update(self, comment: Comment) -> None:
        comment_orm = await self.session.get(CommentORM, comment.id)
        if comment_orm is None:
            msg = f'Comment with id={comment.id} not found'
            raise CommentNotFoundError(msg)
        for field, value in comment.model_dump().items():
            setattr(comment_orm, field, value)
        await self.session.flush()

    @override
    async def delete(self, comment: Comment) -> None:
        comment_orm = await self.session.get(CommentORM, comment.id)
        if comment_orm is None:
            msg = f'Comment with id={comment.id} not found'
            raise CommentNotFoundError(msg)
        await self.session.delete(comment_orm)
        await self.session.flush()

    @override
    async def get_page(self, *, game_id: int, limit: int, offset: int) -> CommentPage:
        filtered = self._filtered(game_id)
        total = await self.session.scalar(select(func.count()).select_from(filtered.subquery()))
        result = await self.session.execute(
            filtered.order_by(CommentORM.created_at, CommentORM.id).limit(limit).offset(offset),
        )
        items = [self._item(comment_orm, user_orm) for comment_orm, user_orm in result.tuples()]
        return CommentPage(items=items, total=total or 0)

    def _filtered(self, game_id: int):
        return (
            select(CommentORM, UserORM)
            .join(UserORM, UserORM.id == CommentORM.user_id)
            .where(CommentORM.game_id == game_id)
        )

    def _item(self, comment_orm: CommentORM, user_orm: UserORM) -> CommentItem:
        comment = comment_orm.to_domain()
        user = user_orm.to_domain()
        return CommentItem(
            uuid=comment.uuid,
            text=comment.text,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            author=CommentAuthor(uuid=user.uuid, nickname=user.nickname, avatar_url=user.avatar_url),
        )
