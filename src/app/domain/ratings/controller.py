from typing import Any
from uuid import UUID

from litestar import Controller, Request, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from ..accounts.models import User
from .dtos import RatingGetDTO, RatingSetDTO
from .services import RatingService


class RatingController(Controller):
    path = "/ratings"
    tags = ["Ratings"]
    service = RatingService()

    @post("/")
    async def set_rating(
        self, data: RatingSetDTO, session: AsyncSession, request: Request[User, Any, Any]
    ) -> RatingSetDTO:
        return await self.service.set_rating(
            session=session,
            rating=data,
            author_id=request.user.id
        )

    @get(path="/{question_id:uuid}/user/{user_id:uuid}")
    async def get_rating(self, session: AsyncSession, user_id: UUID, question_id: UUID) -> RatingGetDTO | None:
        return await self.service.get_rating(user_id=user_id, question_id=question_id, session=session)
