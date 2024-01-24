from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .dtos import CommentCreate
from .models import Comment


class CommentsService:
    @staticmethod
    async def get_comments(session: AsyncSession, quesion_id: UUID) -> Sequence[Comment]:
        return (await session.scalars(select(Comment).where(Comment.question_id == quesion_id))).all()

    @staticmethod
    async def create_comment(session: AsyncSession, author_id: UUID, data: CommentCreate) -> Comment:
        comment = Comment(author_id=author_id, question_id=data.question_id, comment=data.comment)
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return await session.scalar(
            select(Comment).where(Comment.id == comment.id).options(selectinload(Comment.author))
        )
