from litestar import Controller, get
from litestar.status_codes import HTTP_200_OK
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .dtos import CommentGetDTO, CommentDTO
from .models import Comment


class CommentController(Controller):
    path = "/comments"
    tags = ["Comments"]

    @get("/", return_dto=CommentDTO, status_code=HTTP_200_OK)
    async def get_comments(self, session: AsyncSession) -> Comment:
        return await session.scalar(select(Comment))
