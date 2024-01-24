from typing import Annotated, Any, Sequence, TypeVar
from uuid import UUID

from litestar import Controller, Request, get, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..accounts.models import User
from .dtos import CommentCreate, CommentCreateDTO, CommentDTO
from .models import Comment
from .services import CommentsService

T = TypeVar("T")
JsonEncoded = Annotated[T, Body(media_type=RequestEncodingType.JSON)]


class CommentController(Controller):
    path = "/comments"
    tags = ["Comments"]

    @get("/", return_dto=CommentDTO, status_code=HTTP_200_OK)
    async def get_comments(self, session: AsyncSession) -> Sequence[Comment]:
        return (await session.scalars(select(Comment).options(selectinload(Comment.author)))).all()

    @get("/{question_id:uuid}", return_dto=CommentDTO, status_code=HTTP_200_OK)
    async def get_comment(self, session: AsyncSession, question_id: UUID) -> Sequence[Comment]:
        return (
            await session.scalars(
                select(Comment).where(Comment.question_id == question_id).options(selectinload(Comment.author))
            )
        ).all()

    @post("/", dto=CommentCreateDTO, return_dto=CommentDTO)
    async def create_comment(
        self, session: AsyncSession, data: JsonEncoded[CommentCreate], request: Request[User, Any, Any]
    ) -> Comment:
        return await CommentsService.create_comment(session=session, author_id=request.user.id, data=data)
